(async () => {
    try {
        // Fetch CSV data
        const csvData = await fetch('country_user_gain.csv').then(response => response.text());

        // Fetch the map data
        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());

        // Create the chart
        Highcharts.mapChart('container3', {
            chart: {
                map: topology,
                
            },

            title: {
                text: 'Steam User % Growth Over Three Years (2019–2021)',
                align: 'left'
            },

            credits: {
                href: 'https://steamcommunity.com/sharedfiles/filedetails/?id=923012519',
                mapText: ' Data source: Steam'
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    verticalAlign: 'bottom'
                }
            },

            colorAxis: {
                min: 0,
                stops: [
                    [0, '#f7a35c'],  // Light orange for low values
                    [0.25, '#ffcc99'], // Lighter red
                    [0.5, '#ff6666'],  // Red-orange
                    [0.75, '#ff0000'], // Bright red for higher values
                    [1, '#800000']   // Dark red for the highest values
                ],
            },

            data: {
                csv: csvData, // Use the local CSV file data
                seriesMapping: [{
                    code: 1,   // Assuming country codes are in the second column
                    value: 2   // Assuming user count is in the third column
                }]
            },

            tooltip: {
                valueDecimals: 0,
                valueSuffix: ' %'
            },

            series: [{
                name: 'Steam Users',
                joinBy: ['iso-a3', 'code'],
                dataLabels: {
                    enabled: true,
                    format: '{point.value:.0f}',
                    filter: {
                        operator: '>',
                        property: 'labelrank',
                        value: 250
                    },
                    style: {
                        fontWeight: 'normal'
                    }
                }
            }]
        });


    } catch (error) {
        console.error("Error loading data:", error);
    }
})();

