(async () => {
    try {
        // Lấy dữ liệu CSV
        const csvData = await fetch('country_user_gain.csv').then(response => response.text());

        // Lấy dữ liệu bản đồ
        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());

        // Tạo biểu đồ
        Highcharts.mapChart('container3', {
            chart: {
                map: topology,
                style: {
                    fontFamily: 'MyCustomFont',
                    fontSize: '13px'
                }
            },

            title: {
                text: 'Tăng trưởng người dùng Steam qua ba năm (2019–2021)',
                align: 'left'
            },

            credits: {
                href: 'https://steamcommunity.com/sharedfiles/filedetails/?id=923012519',
                mapText: 'Nguồn dữ liệu: Steam'
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
                    [0, '#f7a35c'],  // Màu cam nhạt cho giá trị thấp
                    [0.25, '#ffcc99'], // Màu đỏ nhạt hơn
                    [0.5, '#ff6666'],  // Màu đỏ cam
                    [0.75, '#ff0000'], // Màu đỏ sáng cho giá trị cao hơn
                    [1, '#800000']   // Màu đỏ đậm cho giá trị cao nhất
                ],
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
                valueSuffix: ' %'
            },

            series: [{
                name: 'Người dùng Steam',
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

