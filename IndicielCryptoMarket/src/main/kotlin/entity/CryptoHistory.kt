package entity

class CryptoHistory {
    var name: String = ""
    var days: MutableList<Day> = arrayListOf()

    override fun toString(): String {
        return name
    }
}

data class Day(
    var name: String = "",
    var date: Long = -1,
    var price: Double = 0.0,
    var market_cap: Long = -1,
    var total_market_cap: Long = -1,
    var top_position: Int = -1,
    var daily_delta: Double = 0.0,
    var weekly_delta: Double = 0.0,
    var monthly_delta: Double = 0.0
)
