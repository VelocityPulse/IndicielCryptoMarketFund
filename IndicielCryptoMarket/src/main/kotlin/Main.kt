fun main(args: Array<String>) {
    println("Hello World!")

    // Try adding program arguments via Run/Debug configuration.
    // Learn more about running applications: https://www.jetbrains.com/help/idea/running-applications.html.
    println("Program arguments: ${args.joinToString()}")

    if (args.isNotEmpty()) {
        val f = Process()
        if ("fetch_data" == args[0])
            f.fetchData()

        if ("calculate" == args[0])
            f.calculatePositions()

    }

}