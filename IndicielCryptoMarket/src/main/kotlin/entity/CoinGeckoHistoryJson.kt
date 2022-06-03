package entity

class CoinGeckoHistoryJson {
    var prices: MutableList<MutableList<Float>> = arrayListOf()
    var market_caps: MutableList<MutableList<Float>> = arrayListOf()
    var total_volumes: MutableList<MutableList<Float>> = arrayListOf()
}