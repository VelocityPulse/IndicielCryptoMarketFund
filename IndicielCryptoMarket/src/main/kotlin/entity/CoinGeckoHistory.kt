package entity

class CoinGeckoHistory {
    var id: String = ""
    var symbol: String = ""
    var market_data: MarketData = MarketData()
}

class MarketData {
    var current_price: HashMap<String, Double> = hashMapOf()
    var market_cap: HashMap<String, Double> = hashMapOf()
    var total_volume: HashMap<String, Double> = hashMapOf()
}
