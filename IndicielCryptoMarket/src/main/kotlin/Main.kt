fun main(args: Array<String>) {
    println("Hello World!")

    // Try adding program arguments via Run/Debug configuration.
    // Learn more about running applications: https://www.jetbrains.com/help/idea/running-applications.html.
    println("Program arguments: ${args.joinToString()}")

    if (args.isNotEmpty()) {
        if ("fetch_data" == args[0])
            FetchData().apply {
                this.fetchData()
//                this.calculatePositions()
            }
        else if ("simulation" == args[0])
            println("use python")
    }

}