import com.google.gson.Gson
import entity.CoinGeckoHistoryJson
import entity.CustomHistoryJson
import entity.Day
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import java.io.IOException
import java.net.URL
import java.nio.file.Files
import java.nio.file.Paths

class FetchData {

    private val dataPath = "./data/"
    private val symbolsPath = "symbols/"
    private val currencyList = "currency_list"
    private val stableCoins =
        arrayListOf("busd", "usdt", "usdc", "dai", "tusd", "usdp", "usdn", "usdd", "fei")

    private val additionalCoins =
        arrayListOf("terra-luna")

    private fun getURLText(link: String): String {
        val url = URL(link)

        while (true) {
            try {
                return url.readText()
            } catch (e: IOException) {
                println("error code : " + e.message + " WAITING DELAY")
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

        val r = getURLText(currencyListUrl)

        Files.createDirectories(Paths.get(dataPath))
        File(dataPath + currencyList).writeText(r)
    }

    private fun loopCurrencyList() {
        val file = File(dataPath + currencyList)
        val json = Json.parseToJsonElement(file.readText()).jsonArray

        val s = Semaphore(2)
        val jobList = mutableListOf<Job>()

        jobList.add(CoroutineScope(Dispatchers.IO).launch {
            s.acquire()

            for (elem in json) {
                if (stableCoins.contains(elem.jsonObject["symbol"].toString()))
                    continue
                downloadCryptoData(elem.jsonObject["id"]!!.jsonPrimitive.content)
            }

            for (elem in additionalCoins)
                downloadCryptoData(elem)
        })

        var jobStillWorking = 1
        while (jobStillWorking > 0) {
            Thread.sleep(3000)
            jobStillWorking = 0
            jobList.forEach {
                jobStillWorking += if (it.isActive) 1 else 0
            }
        }

        jobList
    }

    private fun downloadCryptoData(currency: String) {
        val param1 = "vs_currency=usd&"
        val param2 = "days=max&"
        val param3 = "interval=daily&"

        val url = "https://api.coingecko.com/api/v3/coins/$currency/market_chart/?$param1$param2$param3"
        println(url)

        val r = getURLText(url)

        Files.createDirectories(Paths.get(dataPath + symbolsPath))

        val purifiedJson = purifyJson(r, currency)
        File(dataPath + symbolsPath + currency).writeText(purifiedJson)
    }

    @Suppress("UNCHECKED_CAST", "SENSELESS_COMPARISON")
    private fun purifyJson(content: String, currency: String): String {

        val j: CoinGeckoHistoryJson = Gson().fromJson(content, CoinGeckoHistoryJson::class.java)

        // Fix market_caps

        val newValues = CustomHistoryJson()

        for (i in 0 until j.prices.size) {
            try {
                j.market_caps[i][1].toLong() // Prevent empty value by accessing it a first time
            } catch (e: Throwable) {
                j.market_caps[i].add(1, j.market_caps[i - 1][1])
            }

            val day = Day(
                date = j.prices[i][0].toLong(),
                price = j.prices[i][1].toDouble(),
                market_cap = j.market_caps[i][1].toLong()
            ).apply {
                if (market_cap == 0L && i > 0)
                    market_cap = j.market_caps[i - 1][1].toLong();
            }
            newValues.days.add(i, day)
        }
        newValues.name = currency
        return Gson().toJson(newValues)
    }

    fun fetchData() {
        println("Fetch data")

        File(dataPath).deleteRecursively()

        downloadCurrencyList()

        loopCurrencyList()
    }
}