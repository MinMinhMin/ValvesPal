
document.addEventListener('DOMContentLoaded', function () {
    var chartConfig1 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "So s\u00e1nh gi\u00e1 tr\u1ecb l\u1edbn nh\u1ea5t cho m\u1ed7i c\u1eeda h\u00e0ng (H\u00e0ng th\u00e1ng)", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "GOG_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "GreenManGaming_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "Humble Store_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}]};
    var chartConfig2 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "So s\u00e1nh gi\u00e1 tr\u1ecb nh\u1ecf nh\u1ea5t cho m\u1ed7i c\u1eeda h\u00e0ng (H\u00e0ng th\u00e1ng)", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 26.99, 26.99]}, {"name": "GOG_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99]}, {"name": "GreenManGaming_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 26.99, 26.99]}, {"name": "Humble Store_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 26.99, 26.99]}]};
    var chartConfig3 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "So s\u00e1nh gi\u00e1 tr\u1ecb trung b\u00ecnh cho m\u1ed7i c\u1eeda h\u00e0ng (H\u00e0ng th\u00e1ng)", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_avg", "data": [44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 43.49, 43.49]}, {"name": "GOG_avg", "data": [44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99]}, {"name": "GreenManGaming_avg", "data": [44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 43.49, 43.49]}, {"name": "Humble Store_avg", "data": [44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 43.49, 43.49]}]};
    var chartConfig4 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "D\u1ef1 \u0111o\u00e1n gi\u00e1 tr\u1ecb l\u1edbn nh\u1ea5t cho 12 th\u00e1ng ti\u1ebfp theo", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "GOG_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "GreenManGaming_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}, {"name": "Humble Store_max", "data": [59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99, 59.99]}]};
    var chartConfig5 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "D\u1ef1 \u0111o\u00e1n gi\u00e1 tr\u1ecb nh\u1ecf nh\u1ea5t cho 12 th\u00e1ng ti\u1ebfp theo", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99]}, {"name": "GOG_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99]}, {"name": "GreenManGaming_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99]}, {"name": "Humble Store_min", "data": [29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99, 29.99]}]};
    var chartConfig6 = {"chart": {"type": "column", "zoomType": "x", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "title": {"text": "D\u1ef1 \u0111o\u00e1n gi\u00e1 tr\u1ecb trung b\u00ecnh cho 12 th\u00e1ng ti\u1ebfp theo", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "xAxis": {"categories": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"], "title": {"text": "Th\u00e1ng", "style": {"fontFamily": "MyCustomFont, sans-serif"}}, "labels": {"rotation": -45}}, "yAxis": {"title": {"text": "Gi\u00e1 (USD)"}}, "tooltip": {"shared": true, "useHTML": true, "headerFormat": "<em>Th\u00e1ng: {point.key}</em><br/>"}, "legend": {"align": "center", "verticalAlign": "bottom", "layout": "horizontal", "itemDistance": 65, "padding": 20, "itemStyle": {"fontSize": "14px", "fontWeight": null, "color": "black"}}, "series": [{"name": "Fanatical_avg", "data": [43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49]}, {"name": "GOG_avg", "data": [44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99, 44.99]}, {"name": "GreenManGaming_avg", "data": [43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49]}, {"name": "Humble Store_avg", "data": [43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49, 43.49]}]};

    Highcharts.chart('container1', chartConfig1);
    Highcharts.chart('container2', chartConfig2);
    Highcharts.chart('container3', chartConfig3);
    Highcharts.chart('container4', chartConfig4);
    Highcharts.chart('container5', chartConfig5);
    Highcharts.chart('container6', chartConfig6);
});