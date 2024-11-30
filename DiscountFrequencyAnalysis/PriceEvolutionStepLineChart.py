import json
import requests
import datetime
from typing import Dict, List, Union
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX


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
        """
        Hàm khởi tạo đối tượng GameDealFetcher.

        Parameters:
        - api_key (str): Khóa API để truy cập dữ liệu từ IsThereAnyDeal.
        - game_id (str): ID của trò chơi cần lấy dữ liệu.
        - shops_file (str): Đường dẫn tới file JSON chứa thông tin các cửa hàng.
        - country (str): Mã quốc gia, mặc định là "US".
        - shops (str): Danh sách ID cửa hàng, mặc định là "61,35,16,6,20,24,37".
        - since (str): Thời gian bắt đầu lấy dữ liệu (ISO 8601), mặc định là "2023-11-06T00:00:00Z".
        """
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
        """
        Hàm tải dữ liệu cửa hàng từ file JSON.

        Parameters:
        - shops_file (str): Đường dẫn tới file JSON chứa dữ liệu cửa hàng.

        Returns:
        - Một từ điển chứa dữ liệu các cửa hàng.
        """
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        """
        Hàm lấy lịch sử giao dịch từ API.

        Returns:
        - Dữ liệu lịch sử giao dịch dưới dạng danh sách hoặc từ điển.
        """
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        """
        Hàm định dạng lại dữ liệu trả về từ API thành dạng dễ sử dụng cho việc vẽ biểu đồ.

        Parameters:
        - data (Union[List, Dict]): Dữ liệu lịch sử giao dịch nhận được từ API.

        Returns:
        - Một danh sách các từ điển chứa thông tin về từng cửa hàng và giao dịch.
        """
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


class PriceEvolutionLineChart:
    def __init__(self, data):
        """
        Hàm khởi tạo đối tượng PriceEvolutionLineChart.

        Parameters:
        - data (List[Dict]): Dữ liệu các giao dịch từ đối tượng GameDealFetcher.
        """
        self.data = data

    def convert_timestamp(self, timestamp: str) -> int:
        """
        Hàm chuyển đổi timestamp từ định dạng ISO 8601 sang Unix timestamp (milliseconds).

        Parameters:
        - timestamp (str): Thời gian ở định dạng ISO 8601.

        Returns:
        - Unix timestamp (int): Thời gian được chuyển đổi sang Unix timestamp (milliseconds).
        """
        dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)

    def prepare_series_data(self):
        """
        Hàm chuẩn bị dữ liệu cho biểu đồ, bao gồm việc xử lý các giao dịch, tạo khoảng thời gian đầy đủ,
        dự báo giá trị trong tương lai, và phân chia các chuỗi dữ liệu thực tế và dự đoán.

        Returns:
        - series (List[Dict]): Danh sách các chuỗi dữ liệu cho biểu đồ (bao gồm cả dữ liệu thực tế và dự đoán).
        - boundary_timestamp (int): Thời gian ranh giới giữa dữ liệu thực tế và dữ liệu dự đoán.
        """
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

        # Tìm ngày bắt đầu và kết thúc chung cho tất cả các chuỗi dữ liệu
        all_timestamps = []
        for shop in self.data:
            deals = shop["deals"]
            df = pd.DataFrame(deals)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            all_timestamps.extend(df["timestamp"].tolist())

        # Xác định khoảng thời gian bao phủ chung cho tất cả các cửa hàng
        min_date = min(all_timestamps)
        max_date = today

        full_date_range = pd.date_range(start=min_date, end=max_date, freq="D", tz="UTC")

        for i, shop in enumerate(self.data):
            shop_title = shop["shop_title"]
            deals = shop["deals"]

            # Convert sang DataFrame để handling dễ hơn
            df = pd.DataFrame(deals)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df.set_index("timestamp", inplace=True)
            df = df.sort_index()

            # Xóa các nhãn bị trùng lặp bằng cách giữ lại giá trị cuối cùng trong ngày
            df = df[~df.index.duplicated(keep="last")]

            # Reindex lại dataframe để bao gồm tất cả các ngày, điền giá trị thiếu bằng phương pháp forward fill
            df = df.reindex(full_date_range, method="ffill")

            # Dự đoán giá trong tương lai bằng phương pháp HoltWinters
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

            # Thêm đoạn nối bằng nét đứt 
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

            # Thêm vào chuỗi với phần dữ liệu thực tế và dự đoán
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
        """
        Hàm dự đoán giá trong tương lai sử dụng mô hình SARIMAX.

        Parameters:
        - df (DataFrame): Dữ liệu giá thực tế đã được xử lý.
        - periods (int): Số ngày cần dự đoán.

        Returns:
        - forecast_series (Series): Chuỗi dự đoán giá trong tương lai.
        """
        # Thiết lập các tham số của SARIMAX (p, d, q) và (P, D, Q, s)
        p, d, q = 1, 1, 1  # Các tham số của phần ARIMA

        # Khởi tạo và huấn luyện mô hình SARIMAX
        model = SARIMAX(df["price"],
                        order=(p, d, q),
                        seasonal_order= None,
                        enforce_stationarity=False,
                        enforce_invertibility=False)

        model_fit = model.fit(disp=False)

        # Dự đoán cho 'periods' ngày tiếp theo
        forecast = model_fit.forecast(steps=periods)

        # Tạo một pandas Series để trả về dự đoán
        future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=periods, freq='D')
        forecast_series = pd.Series(forecast, index=future_dates)

        return forecast_series

    def generate_highcharts_html(
    self,
    output_file: str = "output/synchronized_step_line_charts_with_forecast.html",
):
        """
        Hàm tạo ra mã HTML cho biểu đồ Highcharts, bao gồm cả dự báo và lịch sử giá của trò chơi.
        
        Parameters:
        - output_file (str): Đường dẫn đến file đầu ra chứa mã HTML của biểu đồ. Mặc định là "output/synchronized_step_line_charts_with_forecast.html".
        
        Returns:
        - Không có giá trị trả về. Hàm sẽ lưu mã HTML vào file `output_file`.
        """
        # Lấy dữ liệu chuỗi và thời gian ranh giới giữa dữ liệu thực tế và dự báo
        series_data, boundary_timestamp = self.prepare_series_data()

        chart_configs = []
        
        # Duyệt qua các chuỗi dữ liệu (bao gồm series thực tế, chuỗi nối và dự báo)
        for i in range(0, len(series_data), 3):
            # Cấu hình cho một biểu đồ
            config = {
                "chart": {
                    "type": "line",  # Loại biểu đồ là line (đường)
                    "zoomType": "x",  # Cho phép zoom vào trục x
                    "step": "left",  # Dữ liệu sẽ được thể hiện dưới dạng step line (đường gấp khúc)
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif"  # Thay đổi phông chữ của biểu đồ
                    },
                },
                "title": {
                    "text": f"Lịch Sử Giá Của {series_data[i]['name']}",  # Tiêu đề biểu đồ
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ tiêu đề
                        "fontSize": "14px",  # Kích thước phông chữ
                    },
                },
                "xAxis": {
                    "type": "datetime",  # Trục x hiển thị theo thời gian
                    "title": {
                        "text": "Date",  # Tiêu đề của trục x
                        "style": {
                            "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của trục x
                            "fontSize": "12px",  # Kích thước phông chữ
                        },
                    },
                    "crosshair": True,  # Hiển thị đường cắt ngang tại điểm dữ liệu
                    "plotLines": [
                        {
                            "value": boundary_timestamp,  # Thời gian ranh giới giữa dữ liệu thực tế và dự báo
                            "color": "red",  # Màu của đường phân cách
                            "width": 2,  # Độ rộng của đường phân cách
                            "dashStyle": "Dash",  # Kiểu đường phân cách là nét đứt
                            "label": {
                                "text": "Thời Gian Hiện Tại",  # Nhãn của đường phân cách
                                "align": "left",  # Vị trí nhãn
                                "rotation": 0,
                                "y": 15,
                                "style": {
                                    "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của nhãn
                                    "fontSize": "10px",  # Kích thước phông chữ của nhãn
                                    "color": "rgba(0, 0, 0, 0.5)",  # Màu sắc của nhãn
                                    "fontWeight": "bold",  # Định dạng phông chữ (đậm)
                                },
                            },
                        }
                    ],
                },
                "yAxis": {
                    "title": {
                        "text": "Giá (USD)",  # Tiêu đề của trục y
                        "style": {
                            "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của trục y
                            "fontSize": "12px",  # Kích thước phông chữ
                        },
                    },
                    "min": 0,  # Giá trị tối thiểu của trục y là 0
                },
                "tooltip": {
                    "valueSuffix": " USD",  # Đơn vị hiển thị khi hover chuột
                    "shared": True,  # Chia sẻ tooltip giữa các chuỗi
                    "crosshairs": True,  # Hiển thị đường cắt ngang khi hover
                    "dateTimeLabelFormats": {"day": "%e %b %Y"},  # Định dạng ngày tháng trong tooltip
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của tooltip
                        "fontSize": "10px",  # Kích thước phông chữ của tooltip
                    },
                },
                "series": [series_data[i], series_data[i + 1], series_data[i + 2]],  # Các chuỗi thực tế, nối và dự báo
                "plotOptions": {
                    "series": {
                        "step": "left",  # Cài đặt kiểu step line
                        "point": {
                            "events": {
                                "mouseOver": None,  # Placeholder cho sự kiện mouseOver
                                "mouseOut": None,  # Placeholder cho sự kiện mouseOut
                            }
                        },
                    }
                },
                "legend": {
                    "itemStyle": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của chú giải (legend)
                        "fontSize": "12px",  # Kích thước phông chữ của legend
                    }
                },
            }
            
            # Thêm cấu hình của biểu đồ vào danh sách chart_configs
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

        for i in range(len(chart_configs)):
            html_content += f'<div id="container-{i}" style="width: 100%; height: 400px; margin: 20px 0;"></div>'

        
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

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"File HTML đã được tạo thành công: {output_file}")
        except Exception as e:
            print(f"Lỗi khi tạo file HTML: {str(e)}")


def main():
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-4008-731e-8860-4f552b359a5c"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    price_evolution_chart = PriceEvolutionLineChart(formatted_data)
    price_evolution_chart.generate_highcharts_html(
        "synchronized_step_line_charts_with_forecast.html"
    )


if __name__ == "__main__":
    main()
