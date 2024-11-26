import json
import requests
import datetime
from typing import Dict, List, Union
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np


class GameDealFetcher:
    def __init__(
        self,
        api_key: str,
        game_id: str,
        shops_file: str,
        country: str = "US",
        shops: str = "61,35,16,6,20,24,37",
        since: str = "2023-11-06T00:00:00Z",
    ):
        self.api_key = api_key
        self.base_url = "https://api.isthereanydeal.com/games/history/v2"
        self.params = {
            "key": self.api_key,
            "id": game_id,
            "country": country,
            "shops": shops,
            "since": since,
        }
        self.shops_data = self.load_shops_data(shops_file)

    def load_shops_data(self, shops_file: str) -> Dict:
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        formatted_data = []

        for item in data:
            shop_id = str(item["shop"]["id"])
            shop_name = self.shops_data.get(shop_id, "Unknown Shop")
            timestamp = item["timestamp"]
            deal_info = {
                "timestamp": timestamp,
                "price": item["deal"]["price"]["amount"],
                "regular_price": item["deal"]["regular"]["amount"],
                "cut": item["deal"]["cut"],
            }

            shop_entry = next(
                (s for s in formatted_data if s["shop_id"] == shop_id), None
            )

            if not shop_entry:
                shop_entry = {"shop_id": shop_id, "shop_title": shop_name, "deals": []}
                formatted_data.append(shop_entry)

            shop_entry["deals"].append(deal_info)

        return formatted_data


import datetime


class PriceEvolutionLineChart:
    def __init__(self, data):
        self.data = data

    def convert_timestamp(self, timestamp: str) -> int:
        dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)

    def prepare_series_data(self):
        series = []
        colors = [
            "#7cb5ec",
            "#434348",
            "#90ed7d",
            "#f7a35c",
            "#8085e9",
            "#f15c80",
            "#e4d354",
        ]

        # Lấy ngày hiện tại
        today = pd.Timestamp.now(tz="UTC").normalize()

        for i, shop in enumerate(self.data):
            shop_title = shop["shop_title"]
            deals = shop["deals"]

            # Convert deals to DataFrame for better handling
            df = pd.DataFrame(deals)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df.set_index("timestamp", inplace=True)
            df = df.sort_index()

            # Xóa các nhãn bị trùng lặp bằng cách giữ lại giá trị cuối cùng trong ngày
            df = df[~df.index.duplicated(keep="last")]

            # Create a date range from the earliest date to today with daily frequency
            full_date_range = pd.date_range(
                start=df.index.min(), end=today, freq="D", tz="UTC"
            )

            # Reindex the dataframe to include all days, forward filling missing values
            df = df.reindex(full_date_range, method="ffill")

            # Dự đoán giá trong tương lai bằng phương pháp Holt-Winters
            df_forecast = self.forecast_prices(df, periods=120)

            # Phân chia dữ liệu thực tế và dự đoán cho biểu diễn khác nhau
            series_data_real = [
                [int(ts.timestamp() * 1000), row] for ts, row in df["price"].items()
            ]
            series_data_forecast = [
                [int(ts.timestamp() * 1000), row] for ts, row in df_forecast.items()
            ]

            # Đánh dấu ranh giới giữa dữ liệu thực tế và dự đoán
            boundary_timestamp = int(df.index[-1].timestamp() * 1000)

            # Thêm đoạn nối bằng nét đứt giữa dữ liệu thực tế và dự đoán
            connecting_line = [
                [
                    series_data_real[-1][0],
                    series_data_real[-1][1],
                ],  # Điểm cuối cùng của dữ liệu thực tế
                [
                    series_data_forecast[0][0],
                    series_data_forecast[0][1],
                ],  # Điểm đầu tiên của dự đoán
            ]

            # Thêm vào series với phần dữ liệu thực tế và dự đoán
            series.append(
                {
                    "name": shop_title,
                    "data": series_data_real,
                    "color": colors[i % len(colors)],
                    "dashStyle": "Solid",
                }
            )

            # Thêm đoạn nối
            series.append(
                {
                    "name": f"{shop_title} (Dự đoán)",
                    "data": connecting_line,
                    "color": colors[i % len(colors)],
                    "dashStyle": "Dash",
                    "enableMouseTracking": True,
                    "marker": {"enabled": True},
                    "showInLegend": False,
                }
            )

            # Thêm phần dự báo với nét đứt
            series.append(
                {
                    "name": f"{shop_title} (Dự đoán)",
                    "data": series_data_forecast,
                    "color": colors[i % len(colors)],
                    "dashStyle": "Dash",
                }
            )

        return series, boundary_timestamp

    def forecast_prices(self, df, periods=120):
        # Áp dụng mô hình Holt-Winters để dự đoán
        if len(df) < 2:
            raise ValueError("Không đủ dữ liệu để dự đoán")

        model = ExponentialSmoothing(
            df["price"], trend="add", seasonal=None, seasonal_periods=7
        )
        model_fit = model.fit()
        forecast = model_fit.forecast(periods)
        forecast_index = pd.date_range(
            start=df.index[-1] + pd.Timedelta(days=1),
            periods=periods,
            freq="D",
            tz="UTC",
        )
        forecast_series = pd.Series(forecast, index=forecast_index, name="price")

        return forecast_series

    def generate_highcharts_html(
        self,
        output_file: str = "output/synchronized_step_line_charts_with_forecast.html",
    ):
        series_data, boundary_timestamp = self.prepare_series_data()

        chart_configs = []
        for i in range(
            0, len(series_data), 3
        ):  # Loop through real, connecting, and forecast series
            config = {
                "chart": {
                    "type": "line",
                    "zoomType": "x",
                    "step": "left",  # Chuyển đồ thị thành kiểu step line với góc bo vuông
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif"  # Thay đổi phông chữ của biểu đồ
                    },
                },
                "title": {
                    "text": f"Lịch Sử Giá Của {series_data[i]['name']}",
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của tiêu đề
                        "fontSize": "14px",
                    },
                },
                "xAxis": {
                    "type": "datetime",
                    "title": {
                        "text": "Date",
                        "style": {
                            "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của trục x
                            "fontSize": "12px",
                        },
                    },
                    "crosshair": True,
                    "plotLines": [
                        {
                            "value": boundary_timestamp,
                            "color": "red",
                            "width": 2,
                            "dashStyle": "Dash",
                            "label": {
                                "text": "Thời Gian Hiện Tại",
                                "align": "left",
                                "rotation": 0,
                                "y": 15,
                                "style": {
                                    "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của nhãn
                                    "fontSize": "10px",
                                    "color": "rgba(0, 0, 0, 0.5)",
                                    "fontWeight": "bold",
                                },
                            },
                        }
                    ],
                },
                "yAxis": {
                    "title": {
                        "text": "Giá (USD)",
                        "style": {
                            "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của trục y
                            "fontSize": "12px",
                        },
                    },
                    "min": 0,
                },
                "tooltip": {
                    "valueSuffix": " USD",
                    "shared": True,
                    "crosshairs": True,
                    "dateTimeLabelFormats": {"day": "%e %b %Y"},
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của tooltip
                        "fontSize": "10px",
                    },
                },
                "series": [series_data[i], series_data[i + 1], series_data[i + 2]],
                "plotOptions": {
                    "series": {
                        "step": "left",  # Cài đặt kiểu step line để tạo góc bo vuông cho dữ liệu
                        "point": {
                            "events": {
                                "mouseOver": None,  # Placeholder for mouseOver event
                                "mouseOut": None,  # Placeholder for mouseOut event
                            }
                        },
                    }
                },
                "legend": {
                    "itemStyle": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Thay đổi phông chữ của chú giải (legend)
                        "fontSize": "12px",
                    }
                },
            }
            chart_configs.append(config)

        # Start building the HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Synchronized Game Deal Charts with Forecast</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
            <script src="https://code.highcharts.com/modules/export-data.js"></script>
        <style>
            @font-face {
                font-family: 'MyCustomFont';
                src: url('../FVF_Fernando_08.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }

            body {
                font-family: 'MyCustomFont', sans-serif;
            }
            ::-webkit-scrollbar {
                            width: 12px;
                            background: black;
                            margin: 15px 0 15px 0;
                            border-radius: 0px;
                        }

                        /* Style cho tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb {
                            background-color: white;
                            min-height: 30px;
                            border-radius: 7px;
                            border: 3px solid black;
                        }

                        /* Hover trên tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:hover {
                            background-color: silver;
                        }

                        /* Nhấn tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:active {
                            background-color: rgb(185, 0, 92);
                        }

                        /* Style cho nút cuộn lên */
                        ::-webkit-scrollbar-button:vertical:increment {
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-top-left-radius: 7px;
                            border-top-right-radius: 7px;
                        }

                        /* Style cho nút cuộn xuống */
                        ::-webkit-scrollbar-button:vertical:decrement {
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-bottom-left-radius: 7px;
                            border-bottom-right-radius: 7px;
                        }

                        /* Ẩn các mũi tên */
                        ::-webkit-scrollbar-button {
                            background: none;
                        }

                        /* Cấm các phần trang (khu vực không phải tay cầm) */
                        ::-webkit-scrollbar-track-piece {
                            background: none;
                        }
        </style>
        </head>
        <body>
        <div id="container"></div>
        """

        # Create the div container for each chart
        for i in range(len(chart_configs)):
            html_content += f'<div id="container-{i}" style="width: 100%; height: 400px; margin: 20px 0;"></div>'

        # JavaScript to create and synchronize charts
        html_content += """
        <script>
        let charts = [];

        document.addEventListener('DOMContentLoaded', function () {
        """
        for i, config in enumerate(chart_configs):
            html_content += f"""
            const config_{i} = {json.dumps(config)};
            const chart_{i} = Highcharts.chart('container-{i}', config_{i});
            charts.push(chart_{i});
            """

        # JavaScript for synchronized zoom, highlight, and tooltips
        html_content += """
            // Synchronize tooltips and crosshairs across all charts
            ['mousemove', 'touchmove', 'touchstart'].forEach(function (eventType) {
                document.addEventListener(eventType, function (e) {
                    let chart, point, i, event;

                    for (i = 0; i < charts.length; i++) {
                        chart = charts[i];
                        // Find coordinates within the chart
                        event = chart.pointer.normalize(e);
                        // Get the hovered point from each series
                        point = chart.series.reduce((acc, series) => {
                            const p = series.searchPoint(event, true);
                            return p && (!acc || Math.abs(p.plotX - event.chartX) < Math.abs(acc.plotX - event.chartX)) ? p : acc;
                        }, null);

                        if (point) {
                            point.highlight(e);
                        }
                    }
                });
            });

            Highcharts.Pointer.prototype.reset = function () {
                return undefined;
            };

            Highcharts.Point.prototype.highlight = function (event) {
                event = this.series.chart.pointer.normalize(event);
                this.onMouseOver(); // Show the hover marker
                this.series.chart.tooltip.refresh(this); // Show the tooltip
                this.series.chart.xAxis[0].drawCrosshair(event, this); // Show the crosshair
            };

            // Synchronize the zooming across all charts
            function syncExtremes(e) {
                const thisChart = this.chart;

                if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
                    Highcharts.each(charts, function (chart) {
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

            // Assign setExtremes event handler to each chart's xAxis
            Highcharts.each(charts, function (chart) {
                chart.xAxis[0].update({
                    events: {
                        setExtremes: syncExtremes
                    }
                });
            });

            // Synchronize zoom reset across all charts
            function resetZoom() {
                Highcharts.each(charts, function (chart) {
                    chart.xAxis[0].setExtremes(null, null, true, false);
                });
            }

            // Add reset button to reset all charts zoom
            const resetButton = document.createElement('button');
            resetButton.innerHTML = 'Reset Zoom';
            resetButton.style.fontFamily = 'MyCustomFont, sans-serif';
            resetButton.style.display = 'block';
            resetButton.style.margin = '20px auto';
            resetButton.addEventListener('click', resetZoom);
            document.body.insertBefore(resetButton, document.getElementById('container'));

            // Add selection resetZoom behavior for each chart
            Highcharts.each(charts, function (chart) {
                chart.update({
                    chart: {
                        events: {
                            selection: function (e) {
                                if (!e.resetSelection) {
                                    syncExtremes.call(this.xAxis[0], e);
                                } else {
                                    resetZoom();
                                }
                            }
                        }
                    }
                });
            });
        });
        </script>
        </body>
        </html>
        """

        # Write the HTML content to a file
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"File HTML đã được tạo thành công: {output_file}")
        except Exception as e:
            print(f"Lỗi khi tạo file HTML: {str(e)}")


def main():
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-4008-731e-8860-4f552b359a5c"
    shops_file = "shops.json"

    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    price_evolution_chart = PriceEvolutionLineChart(formatted_data)
    price_evolution_chart.generate_highcharts_html(
        "synchronized_step_line_charts_with_forecast.html"
    )


if __name__ == "__main__":
    main()
