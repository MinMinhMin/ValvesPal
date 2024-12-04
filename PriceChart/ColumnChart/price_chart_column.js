
document.addEventListener('DOMContentLoaded', function () {
    var chartConfig1 = {"chart": {"type": "column", "style": {"fontFamily": "MyCustomFont"}}, "title": {"text": "T\u1ed5ng ti\u1ebft ki\u1ec7m t\u1eeb gi\u1ea3m gi\u00e1 cho m\u1ed7i c\u1eeda h\u00e0ng (L\u1ecbch s\u1eed)", "style": {"fontFamily": "MyCustomFont"}}, "xAxis": {"categories": ["GreenManGaming", "Humble Store", "Fanatical", "GOG"], "title": {"text": "C\u1eeda h\u00e0ng"}}, "yAxis": {"title": {"text": "T\u1ed5ng ti\u1ebft ki\u1ec7m (USD)"}}, "series": [{"name": "T\u1ed5ng ti\u1ebft ki\u1ec7m", "data": [423.0, 297.0, 393.0, 330.0]}]};
    var chartConfig2 = {"chart": {"type": "column", "style": {"fontFamily": "MyCustomFont"}}, "title": {"text": "D\u1ef1 \u0111o\u00e1n t\u1ed5ng ti\u1ebft ki\u1ec7m t\u1eeb gi\u1ea3m gi\u00e1 cho m\u1ed7i c\u1eeda h\u00e0ng (4 th\u00e1ng ti\u1ebfp theo)", "style": {"fontFamily": "MyCustomFont"}}, "xAxis": {"categories": ["GreenManGaming", "Humble Store", "Fanatical", "GOG"], "title": {"text": "C\u1eeda h\u00e0ng"}}, "yAxis": {"title": {"text": "T\u1ed5ng ti\u1ebft ki\u1ec7m (USD)"}}, "series": [{"name": "T\u1ed5ng ti\u1ebft ki\u1ec7m", "data": [574.56, 428.98, 536.62, 499.29]}]};

    Highcharts.chart('container1', chartConfig1);
    Highcharts.chart('container2', chartConfig2);
});

