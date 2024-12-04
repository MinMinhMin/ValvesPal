(async () => {
    try {
        // Lấy dữ liệu CSV
        const csvData = await fetch('steam_users_2021_output.csv').then(response => response.text());

        // Lấy dữ liệu bản đồ
        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());

        // Tạo biểu đồ
        Highcharts.mapChart('container2', {
            chart: {
            map: topology,
            style: {
                fontFamily: 'MyCustomFont',
                fontSize: '13px'
            }
            },

            title: {
            text: 'Số lượng người dùng Steam theo quốc gia (2021)',
            align: 'left'
            },

            credits: {
            href: 'https://steamcommunity.com/sharedfiles/filedetails/?id=923012519',
            text: 'Nguồn dữ liệu: Steam'
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
            csv: csvData, 
            seriesMapping: [{
                code: 1,   
                value: 2   
            }]
            },

            tooltip: {
            valueDecimals: 0,
            valueSuffix: ' người dùng'
            },

            series: [{
            name: 'Người dùng Steam',
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

