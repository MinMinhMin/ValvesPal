import pandas as pd
import numpy as np
import json
import requests
import datetime
from typing import Dict, List, Union
from collections import defaultdict
from statsmodels.tsa.arima.model import ARIMA


# Class GameDealFetcher để lấy dữ liệu từ API
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
        # Khởi tạo với các tham số cần thiết như api_key, game_id, file JSON chứa danh sách shop, quốc gia, cửa hàng và ngày bắt đầu lấy dữ liệu
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
        # Đọc file JSON chứa thông tin các cửa hàng
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        # Gửi yêu cầu đến API để lấy dữ liệu giảm giá
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        # Định dạng lại dữ liệu để dễ xử lý
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        formatted_data = []

        for item in data:
            # Lấy ID của shop và tìm tên shop từ dữ liệu shops_data
            shop_id = str(item["shop"]["id"])
            shop_name = self.shops_data.get(shop_id, "Unknown Shop")
            timestamp = item["timestamp"]
            deal_info = {
                "timestamp": timestamp,
                "price": item["deal"]["price"]["amount"],
                "regular_price": item["deal"]["regular"]["amount"],
                "cut": item["deal"]["cut"],
            }

            # Kiểm tra xem cửa hàng này đã có trong formatted_data chưa
            shop_entry = next(
                (s for s in formatted_data if s["shop_id"] == shop_id), None
            )

            # Nếu chưa, thêm cửa hàng vào formatted_data
            if not shop_entry:
                shop_entry = {"shop_id": shop_id, "shop_title": shop_name, "deals": []}
                formatted_data.append(shop_entry)

            # Thêm thông tin deal vào danh sách các deal của cửa hàng đó
            shop_entry["deals"].append(deal_info)

        return formatted_data


# Class DiscountFrequencyHeatmap để tạo biểu đồ Heatmap
class DiscountFrequencyHeatmap:
    def __init__(self, shops_data: List[Dict]):
        # Khởi tạo với dữ liệu cửa hàng đã được định dạng
        self.shops_data = shops_data

    def process_raw_data(self) -> Dict:
        # Xử lý dữ liệu thô để tạo ra tần suất giảm giá
        discount_frequency = defaultdict(lambda: defaultdict(int))
        for shop in self.shops_data:
            shop_title = shop["shop_title"]

            # Duyệt qua tất cả các deal của từng cửa hàng
            for deal in shop["deals"]:
                date = datetime.datetime.fromisoformat(deal["timestamp"]).strftime(
                    "%Y-%m"
                )
                discount = deal["cut"]
                # Tăng giá trị tần suất cho mức giảm giá nhất định của tháng đó
                if deal["cut"] > 0:
                    discount_frequency[(shop_title, date)][discount] += 1

        heatmap_data = []
        # Lấy danh sách cửa hàng và danh sách tháng
        shop_titles = sorted({shop["shop_title"] for shop in self.shops_data})
        dates = sorted({date for (_, date) in discount_frequency.keys()})

        # Tạo dữ liệu cho heatmap dựa trên tần suất giảm giá
        for i, shop in enumerate(shop_titles):
            for j, date in enumerate(dates):
                total_frequency = sum(discount_frequency[(shop, date)].values())
                heatmap_data.append([i, j, total_frequency])

        return {
            "shop_titles": shop_titles,
            "dates": dates,
            "heatmap_data": heatmap_data,
            "discount_frequency": discount_frequency,
        }

    def predict_next_three_months(self, discount_frequency: defaultdict, last_date: str) -> List[List[int]]:
        # Dự đoán tần suất giảm giá trong ba tháng tiếp theo
        shop_titles = sorted({shop["shop_title"] for shop in self.shops_data})
        dates = pd.to_datetime(
            sorted({date for (_, date) in discount_frequency.keys()})
        )

        # Xác định ba tháng tiếp theo từ tháng cuối cùng
        next_three_months = []
        last_month = pd.to_datetime(last_date)

        for i in range(1, 4):
            next_month = (last_month + pd.DateOffset(months=i)).strftime("%Y-%m")
            next_three_months.append(next_month)

        predictions = []

        # Dự đoán tần suất cho từng cửa hàng
        for i, shop in enumerate(shop_titles):
            shop_data = [
                sum(discount_frequency[(shop, date.strftime("%Y-%m"))].values())
                for date in dates
            ]
            
            if len(shop_data) > 1:
                # Chuyển dữ liệu thành dạng mảng numpy
                shop_data = np.array(shop_data)
                
                # Sử dụng ARIMA để dự đoán
                try:
                    # ARIMA(p, d, q): p = autoregressive, d = differencing, q = moving average
                    model = ARIMA(shop_data, order=(1, 1, 1))  # Tùy chỉnh order (p, d, q) nếu cần
                    model_fit = model.fit()

                    # Dự đoán giá trị cho 3 tháng tiếp theo
                    forecast = model_fit.forecast(steps=3)
                    # Lưu kết quả dự đoán, làm tròn và đảm bảo giá trị không âm
                    predictions.extend(
                        [
                            [i, len(dates) + j, max(0, int(round(pred)))]
                            for j, pred in enumerate(forecast)
                        ]
                    )
                except Exception as e:
                    print(f"Error with ARIMA prediction for {shop}: {e}")
                    # Nếu có lỗi, dự đoán mặc định là 0
                    predictions.extend([[i, len(dates) + j, 0] for j in range(3)])
            else:
                # Nếu không có đủ dữ liệu, dự đoán mặc định là 0
                predictions.extend([[i, len(dates) + j, 0] for j in range(3)])

        return predictions, next_three_months

    def generate_chart_config(self):
        # Tạo cấu hình biểu đồ heatmap cho dữ liệu lịch sử và dữ liệu dự đoán
        processed_data = self.process_raw_data()
        shop_titles = processed_data["shop_titles"]
        dates = processed_data["dates"]
        heatmap_data = processed_data["heatmap_data"]

        # Gọi hàm dự đoán cho ba tháng tiếp theo
        prediction_data, next_three_months = self.predict_next_three_months(
            processed_data["discount_frequency"], dates[-1]
        )
        extended_dates = dates + next_three_months
        prediction_heatmap_data = prediction_data

        # Cấu hình biểu đồ lịch sử
        original_chart_config = {
            "chart": {
                "type": "heatmap",
                "plotBorderWidth": 1,
                "zoomType": "xy",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "title": {
                "text": "Tần suất giảm giá theo cửa hàng trong lịch sử",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "xAxis": {
                "categories": shop_titles,
                "title": {
                    "text": "Cửa Hàng",
                },
                "labels": {"style": {"fontSize": "10px"}},
            },
            "yAxis": {
                "categories": extended_dates,
                "title": {"text": "Tháng"},
                "reversed": True,
                "labels": {"style": {"fontSize": "10px"}},
            },
            "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"},
            "legend": {
                "align": "right",
                "layout": "vertical",
                "margin": 0,
                "verticalAlign": "top",
                "y": 25,
                "symbolHeight": 280,
            },
            "tooltip": {"pointFormat": "Tần Suất Giảm Giá: <b>{point.value}</b>"},
            "series": [
                {
                    "name": "Tần Suất Giảm Giá",
                    "borderWidth": 1,
                    "data": heatmap_data,
                    "dataLabels": {
                        "enabled": True,
                        "color": "#000000",
                        "format": "{point.value}",
                    },
                }
            ],
        }

        # Cấu hình biểu đồ dự đoán
        prediction_chart_config = {
            "chart": {
                "type": "heatmap",
                "plotBorderWidth": 1,
                "zoomType": "xy",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "title": {
                "text": "Dự đoán tần suất giảm giá của các cửa hàng trong ba tháng tiếp theo",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "xAxis": {
                "categories": shop_titles,
                "title": {"text": "Cửa Hàng"},
                "labels": {"style": {"fontSize": "10px"}},
            },
            "yAxis": {
                "categories": extended_dates,
                "title": {"text": "Tháng"},
                "reversed": True,
                "labels": {"style": {"fontSize": "10px"}},
            },
            "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"},
            "legend": {
                "align": "right",
                "layout": "vertical",
                "margin": 0,
                "verticalAlign": "top",
                "y": 25,
                "symbolHeight": 280,
            },
            "tooltip": {
                "pointFormat": "Dự Đoán Tần Suất Giảm Giá: <b>{point.value}</b>"
            },
            "series": [
                {
                    "name": "Dự Đoán Tần Suất Giảm Giá",
                    "borderWidth": 1,
                    "data": prediction_heatmap_data,
                    "dataLabels": {
                        "enabled": True,
                        "color": "#000000",
                        "format": "{point.value}",
                    },
                }
            ],
        }

        return original_chart_config, prediction_chart_config

    def generate_html(self, output_file="heatmap_chart.html"):
        original_chart_config, prediction_chart_config = self.generate_chart_config()
        original_chart_json = json.dumps(original_chart_config)
        prediction_chart_json = json.dumps(prediction_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Biểu Đồ Heatmap - Phân Tích Tần Suất Giảm Giá</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/heatmap.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
        <style>
            @font-face {{
                    font-family: 'MyCustomFont';
                    src: url('../FVF_Fernando_08.ttf') format('truetype');
                    font-weight: normal;
                    font-style: normal;
                }}

                body {{
                    font-family: 'MyCustomFont', sans-serif;
                }}
            ::-webkit-scrollbar {{
                            width: 12px;
                            background: black;
                            margin: 15px 0 15px 0;
                            border-radius: 0px;
                        }}

                        /* Style cho tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb {{
                            background-color: white;
                            min-height: 30px;
                            border-radius: 7px;
                            border: 3px solid black;
                        }}

                        /* Hover trên tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:hover {{
                            background-color: silver;
                        }}

                        /* Nhấn tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:active {{
                            background-color: rgb(185, 0, 92);
                        }}

                        /* Style cho nút cuộn lên */
                        ::-webkit-scrollbar-button:vertical:increment {{
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-top-left-radius: 7px;
                            border-top-right-radius: 7px;
                        }}

                        /* Style cho nút cuộn xuống */
                        ::-webkit-scrollbar-button:vertical:decrement {{
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-bottom-left-radius: 7px;
                            border-bottom-right-radius: 7px;
                        }}

                        /* Ẩn các mũi tên */
                        ::-webkit-scrollbar-button {{
                            background: none;
                        }}

                        /* Cấm các phần trang (khu vực không phải tay cầm) */
                        ::-webkit-scrollbar-track-piece {{
                            background: none;
                        }}
        </style>
        </head>
        <body>
            <div id="container1" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container2" style="width: 100%; height: 500px;"></div>
            <script type="text/javascript">
                function syncExtremes(e) {{
                    var thisChart = this.chart;

                    if (e.trigger !== 'syncExtremes') {{ // Prevent feedback loop
                        Highcharts.each(Highcharts.charts, function (chart) {{
                            if (chart !== thisChart) {{
                                if (chart.xAxis[0].setExtremes) {{ // It is null while updating
                                    chart.xAxis[0].setExtremes(
                                        e.min,
                                        e.max,
                                        undefined,
                                        false,
                                        {{ trigger: 'syncExtremes' }}
                                    );
                                }}
                            }}
                        }});
                    }}
                }}

                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {original_chart_json};
                    var chartConfig2 = {prediction_chart_json};



                    Highcharts.chart('container1', chartConfig1);
                    Highcharts.chart('container2', chartConfig2);
                }});
            </script>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_template)

        print(f"Biểu đồ đã được lưu vào {output_file}")


# Sử dụng GameDealFetcher và DiscountFrequencyHeatmap để tạo biểu đồ Heatmap
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937e-fcfb-7291-bf00-f651841d24d4"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo DiscountFrequencyHeatmap để tạo biểu đồ
    heatmap_chart = DiscountFrequencyHeatmap(formatted_data)
    heatmap_chart.generate_html(
        "heatmap_chart.html"
    )  # Tạo file HTML với biểu đồ Heatmap


if __name__ == "__main__":
    main()
