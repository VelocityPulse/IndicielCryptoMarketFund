import com.google.gson.Gson
import kotlinx.serialization.json.*
import java.io.File
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
        arrayListOf("terra_luna")

    private fun downloadCurrencyList() {
        println("Download currency list")
        val address = "https://api.coingecko.com/api/v3/coins/markets"
        val param1 = "?vs_currency=usd&"
        val param2 = "order=market_cap_desc&"
        val param3 = "include_platform=false"
        val currencyListUrl = address + param1 + param2 + param3

        val r = URL(currencyListUrl).readText()

        Files.createDirectories(Paths.get(dataPath))
        File(dataPath + currencyList).writeText(r)
    }

    private fun loopCurrencyList() {
        val file = File(dataPath + currencyList)
        val json = Json.parseToJsonElement(file.readText()).jsonArray

        for (elem in json) {
            if (stableCoins.contains(elem.jsonObject["symbol"].toString()))
                continue
            downloadCryptoData(elem.jsonObject["id"]!!.jsonPrimitive.content)
        }

        for (elem in additionalCoins)
            downloadCryptoData(elem)
    }

    private fun downloadCryptoData(currency: String) {
        val param1 = "vs_currency=usd&"
        val param2 = "days=max&"
        val param3 = "interval=daily&"

        val url = "https://api.coingecko.com/api/v3/coins/$currency/market_chart/?$param1$param2$param3"
        println(url)

        val r = URL(url).readText()

        Files.createDirectories(Paths.get(dataPath + symbolsPath))

        val purifiedJson = purifyJson(r, currency)
        File(dataPath + symbolsPath + currency).writeText(purifiedJson)
    }

    @Suppress("UNCHECKED_CAST")
    private fun purifyJson(content: String, currency: String): String {
        val j = Gson().fromJson(content, HashMap::class.java)
        j as HashMap<String, Any>





        return ""
    }

    fun fetchData() {
        println("Fetch data")

        File(dataPath).deleteRecursively()

        downloadCurrencyList()

        loopCurrencyList()

    }

}