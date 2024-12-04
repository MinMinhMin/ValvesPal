
function syncExtremes(e) {
    var thisChart = this.chart;

    if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
        Highcharts.each(Highcharts.charts, function (chart) {
            if (chart !== thisChart) {
                if (chart.xAxis[0].setExtremes) { // It is null while updating
                    chart.xAxis[0].setExtremes(
                        e.min,
                        e.max,
                        undefined,
                        false,
                        { trigger: 'syncExtremes' }
                    );
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    var chartConfig1 = {"chart": {"type": "heatmap", "plotBorderWidth": 1, "zoomType": "xy", "style": {"fontFamily": "MyCustomFont"}}, "title": {"text": "T\u1ea7n su\u1ea5t gi\u1ea3m gi\u00e1 theo c\u1eeda h\u00e0ng trong l\u1ecbch s\u1eed", "style": {"fontFamily": "MyCustomFont"}}, "xAxis": {"categories": ["Fanatical", "GOG", "GreenManGaming", "Humble Store"], "title": {"text": "C\u1eeda H\u00e0ng"}, "labels": {"style": {"fontSize": "10px"}}}, "yAxis": {"categories": ["2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02"], "title": {"text": "Th\u00e1ng"}, "reversed": true, "labels": {"style": {"fontSize": "10px"}}}, "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"}, "legend": {"align": "right", "layout": "vertical", "margin": 0, "verticalAlign": "top", "y": 25, "symbolHeight": 280}, "tooltip": {"pointFormat": "T\u1ea7n Su\u1ea5t Gi\u1ea3m Gi\u00e1: <b>{point.value}</b>"}, "series": [{"name": "T\u1ea7n Su\u1ea5t Gi\u1ea3m Gi\u00e1", "borderWidth": 1, "data": [[0, 0, 1], [0, 1, 2], [0, 2, 0], [0, 3, 2], [0, 4, 2], [0, 5, 0], [0, 6, 1], [0, 7, 1], [0, 8, 0], [0, 9, 1], [0, 10, 1], [0, 11, 1], [0, 12, 1], [1, 0, 1], [1, 1, 1], [1, 2, 0], [1, 3, 3], [1, 4, 1], [1, 5, 0], [1, 6, 2], [1, 7, 0], [1, 8, 1], [1, 9, 0], [1, 10, 1], [1, 11, 1], [1, 12, 0], [2, 0, 1], [2, 1, 2], [2, 2, 1], [2, 3, 1], [2, 4, 1], [2, 5, 1], [2, 6, 1], [2, 7, 1], [2, 8, 0], [2, 9, 2], [2, 10, 0], [2, 11, 2], [2, 12, 1], [3, 0, 2], [3, 1, 1], [3, 2, 1], [3, 3, 0], [3, 4, 1], [3, 5, 0], [3, 6, 1], [3, 7, 1], [3, 8, 0], [3, 9, 1], [3, 10, 0], [3, 11, 1], [3, 12, 1]], "dataLabels": {"enabled": true, "color": "#000000", "format": "{point.value}"}}]};
    var chartConfig2 = {"chart": {"type": "heatmap", "plotBorderWidth": 1, "zoomType": "xy", "style": {"fontFamily": "MyCustomFont"}}, "title": {"text": "D\u1ef1 \u0111o\u00e1n t\u1ea7n su\u1ea5t gi\u1ea3m gi\u00e1 c\u1ee7a c\u00e1c c\u1eeda h\u00e0ng trong ba th\u00e1ng ti\u1ebfp theo", "style": {"fontFamily": "MyCustomFont"}}, "xAxis": {"categories": ["Fanatical", "GOG", "GreenManGaming", "Humble Store"], "title": {"text": "C\u1eeda H\u00e0ng"}, "labels": {"style": {"fontSize": "10px"}}}, "yAxis": {"categories": ["2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02"], "title": {"text": "Th\u00e1ng"}, "reversed": true, "labels": {"style": {"fontSize": "10px"}}}, "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"}, "legend": {"align": "right", "layout": "vertical", "margin": 0, "verticalAlign": "top", "y": 25, "symbolHeight": 280}, "tooltip": {"pointFormat": "D\u1ef1 \u0110o\u00e1n T\u1ea7n Su\u1ea5t Gi\u1ea3m Gi\u00e1: <b>{point.value}</b>"}, "series": [{"name": "D\u1ef1 \u0110o\u00e1n T\u1ea7n Su\u1ea5t Gi\u1ea3m Gi\u00e1", "borderWidth": 1, "data": [[0, 13, 1], [0, 14, 1], [0, 15, 1], [1, 13, 1], [1, 14, 1], [1, 15, 1], [2, 13, 1], [2, 14, 1], [2, 15, 1], [3, 13, 1], [3, 14, 1], [3, 15, 1]], "dataLabels": {"enabled": true, "color": "#000000", "format": "{point.value}"}}]};



    Highcharts.chart('container1', chartConfig1);
    Highcharts.chart('container2', chartConfig2);
});
