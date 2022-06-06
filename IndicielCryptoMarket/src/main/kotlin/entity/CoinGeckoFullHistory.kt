package entity

class CoinGeckoFullHistory {
    var prices: MutableList<MutableList<Double>> = arrayListOf()
    var market_caps: MutableList<MutableList<Double>> = arrayListOf()
    var total_volumes: MutableList<MutableList<Double>> = arrayListOf()
}