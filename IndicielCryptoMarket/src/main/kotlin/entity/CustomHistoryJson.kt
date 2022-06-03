package entity

class CustomHistoryJson {
    var name: String = ""
    var days: MutableList<Day> = arrayListOf()
}

data class Day(
    var date: Long = -1,
    var price: Double = 0.0,
    var market_cap: Long = -1,
    var top_position: Int = -1
)
