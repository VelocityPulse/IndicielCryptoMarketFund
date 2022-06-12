import com.google.gson.Gson
import entity.*
import entity.Currency
import kotlinx.coroutines.Job
import java.io.File
import java.io.IOException
import java.net.URL
import java.nio.file.Files
import java.nio.file.Paths
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.abs

class Process {

    private val dataPath = "./data/"
    private val symbolsPath = "symbols/"
    private val processedSymbolsPath = "processedSymbols/"
    private val currencyList = "currency_list"
    private val ignoredCoins =
        arrayListOf("busd", "usdt", "usdc", "dai", "tusd", "usdp", "usdn", "usdd", "fei", "wbtc", "steth")

    private val additionalCoins =
        arrayListOf("terra-luna")

    private fun getURLText(link: String, bypassCode: Int = -1): String? {
        val url = URL(link)

        while (true) {
            try {
                return url.readText()
            } catch (e: IOException) {
                println("error code : " + e.message + " WAITING DELAY")
                if (e.message!!.contains(" $bypassCode "))
                    return null
                Thread.sleep(5000)
            }
        }
    }

    private fun downloadCurrencyList() {
        println("Download currency list")
        val address = "https://api.coingecko.com/api/v3/coins/markets"
        val param1 = "?vs_currency=usd&"
        val param2 = "order=market_cap_desc&"
        val param3 = "include_platform=false"
        val currencyListUrl = address + param1 + param2 + param3

        val r = getURLText(currencyListUrl)!!

        Files.createDirectories(Paths.get(dataPath))
        File(dataPath + currencyList).writeText(r)
    }

    private fun loopCurrencyList() {
        val file = File(dataPath + currencyList)

        val json = Gson().fromJson(file.readText(), Array<Currency>::class.java)

        val jobList = mutableListOf<Job>()

        for (elem in json) {
            elem.symbol
            if (ignoredCoins.contains(elem.symbol))
                continue
            downloadCryptoData(elem.id)
        }

        for (elem in additionalCoins)
            downloadCryptoData(elem)

        var jobStillWorking = 1
        while (jobStillWorking > 0) {
            Thread.sleep(3000)
            jobStillWorking = 0
            jobList.forEach {
                jobStillWorking += if (it.isActive) 1 else 0
            }
        }
    }

    private fun downloadCryptoData(currency: String) {
        val param1 = "vs_currency=usd&"
        val param2 = "days=max&"
        val param3 = "interval=daily&"

        val url = "https://api.coingecko.com/api/v3/coins/$currency/market_chart/?$param1$param2$param3"
        println(url)

        val r = getURLText(url)!!

        Files.createDirectories(Paths.get(dataPath + symbolsPath))

        val purifiedJson = purifyJson(r, currency)
        File(dataPath + symbolsPath + currency).writeText(purifiedJson)
    }

    @Deprecated("")
    private fun retrieveMarketCap(date: Long, currency: String): Long? {

        val param1 = "date=" + SimpleDateFormat("dd-MM-yyyy").format(Date(date))

        val url = "https://api.coingecko.com/api/v3/coins/$currency/history/?$param1"
        println(url)

        val r = getURLText(url, 400) ?: return null
        val json: CoinGeckoHistory = Gson().fromJson(r, CoinGeckoHistory::class.java)

        json.market_data.market_cap["usd"].let {
            if (it == null)
                return null
            return it.toLong()
        }
    }

    private fun checkPurifiedJson(newValues: CryptoHistory) {
        for (day in newValues.days) {
            if (day.market_cap < 1)
                throw AssertionError()
        }
    }

    @Suppress("UNCHECKED_CAST", "SENSELESS_COMPARISON")
    private fun purifyJson(content: String, currency: String): String {

        val j: CoinGeckoFullHistory = Gson().fromJson(content, CoinGeckoFullHistory::class.java)

        val newValues = CryptoHistory()

        for (i in 0 until j.prices.size) {

            try {
                j.market_caps[i][1].toLong() // Prevent empty value by accessing it a first time
                if (j.market_caps[i][1].toLong() == 0L)
                    throw java.lang.IllegalArgumentException()
            } catch (e: Throwable) {
                val fetchedMarketCap = getClosestMarketCap(i, j.market_caps, 4, currency)
                if (fetchedMarketCap == null) {
                    println("Jumping this day")
                    continue
                }
                println("Market cap retrieved: $fetchedMarketCap")
                j.market_caps[i].add(1, fetchedMarketCap.toDouble())
            }

            val day = Day(
                name = currency,
                date = j.prices[i][0].toLong(),
                price = j.prices[i][1],
                market_cap = j.market_caps[i][1].toLong()
            ).apply {
                if (market_cap == 0L)
                    throw java.lang.IllegalArgumentException()
            }
            newValues.days.add(newValues.days.size, day)
        }

        checkPurifiedJson(newValues)
        newValues.name = currency
        return Gson().toJson(newValues)
    }

    private fun getClosestMarketCap(
        offset: Int,
        marketCaps: MutableList<MutableList<Double>>,
        limit: Int,
        currency: String
    ): Long? {
        var result1: Long? = 0L
        var result2: Long? = 0L
        var turn = 0

        while (result1 == 0L && result2 == 0L) {
            println("Researching market-cap for [$currency] turn n°$turn")
            if (turn == limit)
                return null
            turn++

            try {
                result1 = marketCaps[offset + (turn + 1)][1].toLong()
                result2 = marketCaps[offset - (turn - 1)][1].toLong()
            } catch (th: Throwable) {
                if (result1 != 0L)
                    break
            }
        }

        if (result1 != 0L)
            return result1
        return result2
    }

    fun fetchData() {
        println("Fetch data")

        File(dataPath).deleteRecursively()

        downloadCurrencyList()

        loopCurrencyList()
    }

    private fun findOldestCrypto(list: MutableList<CryptoHistory>): CryptoHistory {
        var timeRef = Long.MAX_VALUE
        var ret: CryptoHistory? = null

        for (crypto in list) {
            if (crypto.days[0].date < timeRef) {
                timeRef = crypto.days[0].date
                ret = crypto
            }
        }
        return ret!!
    }

    private fun findCrypto(jsonList: MutableList<CryptoHistory>, name: String): CryptoHistory? {
        for (elem in jsonList) {
            if (elem.name == name)
                return elem
        }
        return null
    }

    private fun findDay(crypto: CryptoHistory, date: Long): Day? {
        for (day in crypto.days) {
            if (day.date == date)
                return day
        }
        return null
    }

    fun calculatePositions() {
        println("Calculate top position")

        val jsonList = mutableListOf<CryptoHistory>()

        val dir = File(dataPath + symbolsPath)
        for (file in dir.listFiles()!!)
            jsonList.add(Gson().fromJson(file.readText(), CryptoHistory::class.java))

        normalizeDates(jsonList)

        val oldestCrypto = findOldestCrypto(jsonList)

        for ((turn, parentDay) in oldestCrypto.days.withIndex()) {
            val presentAtThisDay = mutableListOf<Day>()

            for (crypto in jsonList) {
                for (day in crypto.days) {
                    if (day.date > parentDay.date)
                        break
                    if (day.date == parentDay.date) {
                        presentAtThisDay.add(day)
                        continue
                    }
                }
            }

            presentAtThisDay.sortByDescending {
                it.market_cap
            }

            for ((position, elem) in presentAtThisDay.withIndex()) {

                val crypto = findCrypto(jsonList, elem.name)!!
                for (day in crypto.days) {
                    if (day.date == parentDay.date) {
                        day.top_position = position + 1
                        continue
                    } else
                        continue
                }
            }

            println("Day n° $turn")
        }
        jsonList.sortByDescending { it.days.last().market_cap }


        checkDuplicatedPositions(jsonList)

        println("Writing on disk...")
        File(dataPath + processedSymbolsPath).mkdirs()
        for (elem in jsonList) {
            val jsonText = Gson().toJson(elem)
            File(dataPath + processedSymbolsPath + elem.name).writeText(jsonText)
        }
    }

    private fun normalizeDates(jsonList: MutableList<CryptoHistory>) {
        val oldestCrypto = findOldestCrypto(jsonList)
        var normalizeCount = 0

        val existingCryptoMap = hashMapOf<CryptoHistory, Int>()
        for (parentDay in oldestCrypto.days) {

            for (crypto in jsonList) {
                if (existingCryptoMap.containsKey(crypto))
                    continue
                if (crypto.days[0].date == parentDay.date || crypto.days[0].date < parentDay.date)
                    existingCryptoMap[crypto] = 0 // Adding key
            }

            for (crypto in existingCryptoMap.keys) {
                if (existingCryptoMap[crypto]!! >= crypto.days.size)
                    continue

                // if the crypto day is below 12h from the parent day
                if (abs(crypto.days[existingCryptoMap[crypto]!!].date - parentDay.date) in (1..43200)) {
//                    val actualDifference = crypto.days[existingCryptoMap[crypto]!!].date - parentDay.date
                    normalizeCount++
                    println("Normalizing date n°$normalizeCount")
                    crypto.days[existingCryptoMap[crypto]!!].date = parentDay.date
                }
                existingCryptoMap[crypto] = existingCryptoMap[crypto]!! + 1
            }
        }
    }

    private fun checkDuplicatedPositions(jsonList: MutableList<CryptoHistory>) {
        val oldestCrypto = findOldestCrypto(jsonList)

        for ((turn, parentDay) in oldestCrypto.days.withIndex()) {

            val sameDays = mutableListOf<Day>()
            for (crypto in jsonList) {
                val day = crypto.days.find { day -> day.date == parentDay.date } ?: continue
                sameDays.add(day)
            }

            val positionList = mutableListOf<Int>()

            if (turn == 3304)
                Unit

            for (day in sameDays) {
                if (positionList.contains(day.top_position))
                    throw java.lang.IllegalArgumentException("Top has duplicated position for day n°$turn")
                positionList.add(day.top_position)
            }
        }
    }

    fun calculateDeltas() {
        println("Calculate deltas")

        val jsonList = mutableListOf<CryptoHistory>()

        val dir = File(dataPath + symbolsPath)
        for (file in dir.listFiles()!!)
            jsonList.add(Gson().fromJson(file.readText(), CryptoHistory::class.java))

        val oldestCrypto = findOldestCrypto(jsonList)

        var turn = 0
        for (parentDayDaily in oldestCrypto.days) {
            println("Day n° ${turn++}")
            for (crypto in jsonList) {

                for ((index, day) in crypto.days.withIndex()) {
                    if (day.date == parentDayDaily.date) {
                        if (index > 1)
                            day.daily_delta = (day.price - crypto.days[index - 1].price) / crypto.days[index - 1].price * 100
                        if (index > 7)
                            day.weekly_delta = (day.price - crypto.days[index - 7].price) / crypto.days[index - 7].price * 100
                        if (index > 30)
                            day.monthly_delta = (day.price - crypto.days[index - 30].price) / crypto.days[index - 30].price * 100
                    }
                }
            }
        }
        jsonList.sortByDescending { it.days.last().market_cap }

        println("Writing on disk...")
        File(dataPath + processedSymbolsPath).mkdirs()
        for (elem in jsonList) {
            val jsonText = Gson().toJson(elem)
            File(dataPath + processedSymbolsPath + elem.name).writeText(jsonText)
        }
    }
}























