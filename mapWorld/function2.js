(async () => {
    try {
        // Fetch CSV data
        const csvData = await fetch('steam_users_2021_output.csv').then(response => response.text());

        // Fetch the map data
        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());

        // Create the chart
        Highcharts.mapChart('container2', {
            chart: {
                map: topology,
                
            },

            title: {
                text: 'Steam Users by Country (2021)',
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
                min: 0
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
                valueSuffix: ' users'
            },

            series: [{
                name: 'Steam Users',
                joinBy: ['iso-a3', 'code'],
                dataLabels: {
                    enabled: true,
                    format: '{point.value}',
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

