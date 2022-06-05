package entity

import com.google.gson.annotations.Expose

class CustomHistoryJson {
    var name: String = ""
    var days: MutableList<Day> = arrayListOf()
}

data class Day(
    var name: String = "",
    var date: Long = -1,
    var price: Double = 0.0,
    var market_cap: Long = -1,
    var top_position: Int = -1,
)
