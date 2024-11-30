(async () => {
    try {
        // đọc CSV data
        const csvData = await fetch('steam_users_2019_output.csv').then(response => response.text());

        //  dọc map data
        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());

        // tạo chart
        Highcharts.mapChart('container1', {
            chart: {
            map: topology,
            style: {
                fontFamily: 'MyCustomFont',
                fontSize: '13px'
            }
            },

            title: {
            text: 'Số lượng người dùng Steam theo quốc gia (2019)',
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
            csv: csvData, // Sử dụng dữ liệu tệp CSV cục bộ
            seriesMapping: [{
                code: 1,   // Giả sử mã quốc gia nằm ở cột thứ hai
                value: 2   // Giả sử số lượng người dùng nằm ở cột thứ ba
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

