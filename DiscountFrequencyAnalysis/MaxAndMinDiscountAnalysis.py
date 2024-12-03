import json
import requests
import datetime
from typing import Dict, List, Union
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

# Class GameDealFetcher để lấy dữ liệu từ API
class GameDealFetcher:
    def __init__(
        self,
        api_key: str,  # Khóa API để xác thực truy cập
        game_id: str,  # ID của trò chơi cần lấy thông tin giảm giá
        shops_file: str,  # Đường dẫn đến file JSON chứa danh sách các cửa hàng
        country: str = "US",  # Quốc gia mặc định là "US"
        shops: str = "61,35,16,6,20,24,37",  # Danh sách các ID cửa hàng, ngăn cách bằng dấu phẩy
        since: str = "2023-11-06T00:00:00Z",  # Ngày bắt đầu lấy dữ liệu
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
        """
        Đọc dữ liệu từ file JSON chứa thông tin cửa hàng.

        Parameters:
        - shops_file (str): Đường dẫn đến file JSON chứa thông tin về các cửa hàng.

        Returns:
        - Dict: Từ điển chứa thông tin về cửa hàng.
        """
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        """
        Lấy dữ liệu lịch sử giảm giá từ API.

        Returns:
        - Union[List, Dict]: Dữ liệu giảm giá từ API.
        """
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        """
        Định dạng lại dữ liệu để dễ dàng xử lý.

        Parameters:
        - data (Union[List, Dict]): Dữ liệu thô từ API.

        Returns:
        - List[Dict]: Dữ liệu đã được định dạng.
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


# Class MaximumMinimumDiscountBoxPlot để tạo biểu đồ Box Plot
class MaximumMinimumDiscountBoxPlot:
    def __init__(self, shops_data: List[Dict]):
        """
        Khởi tạo đối tượng MaximumMinimumDiscountBoxPlot.

        Parameters:
        - shops_data (List[Dict]): Danh sách thông tin về các cửa hàng và các giảm giá tương ứng.
        """
        self.shops_data = shops_data

    def process_raw_data(self, raw_data: List[Dict]) -> None:
        """
        Xử lý dữ liệu thô thành dữ liệu phù hợp cho biểu đồ Box Plot.

        Parameters:
        - raw_data (List[Dict]): Dữ liệu thô từ API đã được định dạng.
        """
        self.shops_data = []
        for shop in raw_data:
            shop_title = shop.get("shop_title", "Unknown Shop")
            deals = shop.get("deals", [])
            discounts = [round(deal["cut"], 2) for deal in deals if "cut" in deal]

            self.shops_data.append({"shop_title": shop_title, "discounts": discounts})

    def predict_next_twelve_months(self) -> List[Dict]:
        """
        Dự đoán các mức giảm giá tối đa, tối thiểu trong 12 tháng tiếp theo cho mỗi cửa hàng
        sử dụng mô hình ARIMA.

        Returns:
        - List[Dict]: Dữ liệu dự đoán cho 12 tháng tiếp theo cho mỗi cửa hàng.
        """
        predicted_data = []

        for shop in self.shops_data:
            discounts = shop["discounts"]

            if len(discounts) > 1:  # Đảm bảo có đủ dữ liệu
                # Chuyển đổi dữ liệu giảm giá thành chuỗi thời gian
                discounts_series = pd.Series(discounts)

                # Cố gắng sử dụng ARIMA để dự đoán
                try:
                    # Tạo mô hình ARIMA (sử dụng p=1, d=1, q=1 là lựa chọn ban đầu phổ biến)
                    model = ARIMA(discounts_series, order=(1, 1, 1))
                    model_fit = model.fit()

                    # Dự đoán 12 tháng tiếp theo
                    forecast = model_fit.forecast(steps=12)
                    forecast = [round(max(0, val), 2) for val in forecast]  # Bảo đảm giá trị không âm

                    predicted_data.append(
                        {"shop_title": shop["shop_title"], "discounts": forecast}
                    )
                except Exception as e:
                    # Nếu có lỗi trong việc fitting mô hình ARIMA, sử dụng giá trị mặc định
                    print(f"Error predicting for shop {shop['shop_title']}: {e}")
                    predicted_data.append(
                        {"shop_title": shop["shop_title"], "discounts": [0] * 12}
                    )
            else:
                # Nếu không đủ dữ liệu, dự đoán là 0
                predicted_data.append(
                    {"shop_title": shop["shop_title"], "discounts": [0] * 12}
                )

        return predicted_data

    def generate_chart_config(self, title: str, shop_data: List[Dict]):
        """
        Tạo cấu hình biểu đồ Box Plot.

        Parameters:
        - title (str): Tiêu đề của biểu đồ.
        - shop_data (List[Dict]): Dữ liệu các cửa hàng để tạo biểu đồ.

        Returns:
        - dict: Cấu hình biểu đồ.
        """
        categories = []  # Tên các cửa hàng
        data = []  # Dữ liệu để vẽ biểu đồ box plot
        outliers = []  # Dữ liệu outliers
        mean_values = []  # Giá trị trung bình

        for index, shop in enumerate(shop_data):
            categories.append(shop["shop_title"])
            discounts = shop["discounts"]

            if len(discounts) > 0:
                # Tính toán các giá trị cần thiết cho box plot
                min_discount = min(discounts)
                max_discount = max(discounts)
                lower_quartile = self._calculate_percentile(discounts, 25)
                median = self._calculate_percentile(discounts, 50)
                upper_quartile = self._calculate_percentile(discounts, 75)
                mean_value = sum(discounts) / len(discounts)
                data.append(
                    [min_discount, lower_quartile, median, upper_quartile, max_discount]
                )
                mean_values.append([index, mean_value])

                # Xác định các giá trị outliers
                for value in discounts:
                    if value < lower_quartile - 1.5 * (upper_quartile - lower_quartile) or value > upper_quartile + 1.5 * (
                        upper_quartile - lower_quartile
                    ):
                        outliers.append([index, value])
            else:
                # Nếu không có dữ liệu giảm giá, thêm giá trị mặc định
                data.append([0, 0, 0, 0, 0])

        # Cấu hình biểu đồ Box Plot
        chart_config = {
            "chart": {"type": "boxplot", "style": {"fontFamily": "MyCustomFont"}},
            "title": {"text": title, "style": {"fontFamily": "MyCustomFont"}},
            "xAxis": {"categories": categories, "title": {"text": "Cửa hàng"}},
            "yAxis": {"title": {"text": "Phần trăm giảm giá (%)"}},
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Cửa hàng: {point.key}</em><br/>",
            },
            "series": [
                {
                    "name": "Phân bố giảm giá",
                    "data": data,
                    "tooltip": {
                        "headerFormat": "<em>Phân bố giảm giá của {point.key}</em><br/>"
                    },
                },
                {
                    "name": "Outliers",
                    "type": "scatter",
                    "data": outliers,
                    "marker": {
                        "fillColor": "rgba(223, 83, 83, .5)",
                        "lineWidth": 1,
                        "lineColor": "rgba(223, 83, 83, 1)",
                    },
                    "tooltip": {"pointFormat": "Giá trị ngoại lệ: {point.y}%<br/>"},
                },
                {
                    "name": "Trung bình lý thuyết",
                    "type": "scatter",
                    "data": mean_values,
                    "marker": {
                        "fillColor": "rgba(0, 100, 0, .5)",
                        "lineWidth": 1,
                        "lineColor": "rgba(0, 100, 0, 1)",
                        "radius": 5,
                    },
                    "tooltip": {"pointFormat": "Trung bình lý thuyết: {point.y:.2f}%<br/>"},
                },
            ],
        }

        return chart_config

    @staticmethod
    def _calculate_percentile(data, percentile: float) -> float:
        """
        Tính toán giá trị phần trăm.

        Parameters:
        - data (List[float]): Dữ liệu đầu vào.
        - percentile (float): Giá trị phần trăm cần tính (ví dụ: 25, 50, 75).

        Returns:
        - float: Giá trị phần trăm tương ứng.
        """
        size = len(data)
        sorted_data = sorted(data)
        index = int(round(percentile / 100.0 * (size - 1)))
        return sorted_data[index]

    def generate_html(self, output_file="boxplot_chart.html"):
        """
        Tạo file HTML để hiển thị biểu đồ Box Plot.

        Parameters:
        - output_file (str): Tên của file HTML đầu ra, mặc định là 'boxplot_chart.html'.
        """
        # Tạo cấu hình cho biểu đồ dữ liệu lịch sử
        original_chart_config = self.generate_chart_config(
            "Phân tích giảm giá tối đa và tối thiểu của các cửa hàng (Lịch sử)",
            self.shops_data,
        )
        original_chart_json = json.dumps(original_chart_config)

        # Tạo cấu hình cho biểu đồ dự đoán dữ liệu cho 12 tháng tiếp theo
        predicted_shops_data = self.predict_next_twelve_months()
        predicted_chart_config = self.generate_chart_config(
            "Dự đoán giảm giá tối đa và tối thiểu của các cửa hàng (12 tháng tới)",
            predicted_shops_data,
        )
        predicted_chart_json = json.dumps(predicted_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Box Plot Chart with Predictions</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/highcharts-more.js"></script>
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
                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {original_chart_json};
                    var chartConfig2 = {predicted_chart_json};

                    Highcharts.chart('container1', chartConfig1);
                    Highcharts.chart('container2', chartConfig2);
                }});
            </script>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_template)

        print(f"Chart has been saved to {output_file}")


# Sử dụng GameDealFetcher và MaximumMinimumDiscountBoxPlot để tạo biểu đồ
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo MaximumMinimumDiscountBoxPlot để tạo biểu đồ
    box_plot_chart = MaximumMinimumDiscountBoxPlot([])
    box_plot_chart.process_raw_data(
        formatted_data
    )  # Sử dụng dữ liệu từ GameDealFetcher
    box_plot_chart.generate_html(
        "boxplot_chart.html"
    )  # Tạo file HTML với biểu đồ Box Plot


if __name__ == "__main__":
    main()
