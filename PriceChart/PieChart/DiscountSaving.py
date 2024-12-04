import json
import textwrap
import requests
import datetime
from typing import Dict, List, Union, Tuple
from collections import defaultdict
import numpy as np
from statsmodels.tsa.arima.model import ARIMA


# Class GameDealFetcher để lấy dữ liệu từ API
class GameDealFetcher:
    def __init__(
        self,
        api_key: str,  # Khóa API dùng để truy cập dịch vụ API
        game_id: str,  # ID của trò chơi cần lấy thông tin giảm giá
        shops_file: str,  # Đường dẫn tới file JSON chứa thông tin về các cửa hàng
        country: str = "US",  # Quốc gia áp dụng, mặc định là "US"
        shops: str = "61,35,16,6,20,24,37",  # Danh sách các ID của cửa hàng, ngăn cách bằng dấu phẩy
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
        Đọc dữ liệu từ file JSON chứa thông tin về các cửa hàng.

        Parameters:
        - shops_file (str): Đường dẫn tới file JSON chứa thông tin cửa hàng.

        Returns:
        - Dict: Thông tin cửa hàng dưới dạng từ điển.
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


# Class DiscountSavingsPieChart để tạo biểu đồ Pie Chart
class DiscountSavingsPieChart:
    def __init__(self, shops_data: List[Dict]):
        """
        Khởi tạo đối tượng DiscountSavingsPieChart.

        Parameters:
        - shops_data (List[Dict]): Danh sách thông tin về các cửa hàng và các deal tương ứng.
        """
        self.shops_data = shops_data

    def process_raw_data(self) -> Tuple[Dict[str, float], Dict[str, List[float]]]:
        """
        Tính toán tổng số tiền tiết kiệm và tiết kiệm hàng tháng từ các đợt giảm giá cho mỗi cửa hàng.

        Returns:
        - total_savings (Dict[str, float]): Tổng số tiền tiết kiệm theo từng cửa hàng.
        - monthly_savings (Dict[str, List[float]]): Danh sách tiết kiệm theo từng tháng cho từng cửa hàng.
        """
        total_savings = defaultdict(float)
        savings_per_month = defaultdict(list)

        # Tính số tiền tiết kiệm cho từng deal theo từng tháng
        for shop in self.shops_data:
            shop_title = shop["shop_title"]

            # Tạo một defaultdict với giá trị mặc định là float để lưu tiết kiệm theo tháng
            monthly_savings = defaultdict(float)

            for deal in shop["deals"]:
                timestamp = datetime.datetime.fromisoformat(
                    deal["timestamp"].replace("Z", "+00:00")
                )
                month_key = timestamp.strftime("%Y-%m")  # Lấy tháng và năm (YYYY-MM)

                regular_price = deal["regular_price"]
                discounted_price = deal["price"]
                savings = regular_price - discounted_price

                if savings > 0:
                    monthly_savings[month_key] += savings

            # Tổng tiết kiệm cho cửa hàng này
            total_savings[shop_title] += sum(monthly_savings.values())

            # Chuyển giá trị tiết kiệm hàng tháng thành danh sách để có thể sử dụng cho dự đoán
            sorted_savings = [
                monthly_savings[month] for month in sorted(monthly_savings.keys())
            ]
            savings_per_month[shop_title] = sorted_savings

        return total_savings, savings_per_month

    def predict_next_four_months(
        self, monthly_savings: Dict[str, List[float]]
    ) -> Dict[str, float]:
        predicted_savings = {}

        for shop_title, savings in monthly_savings.items():
            # Kiểm tra số lượng dữ liệu, ít nhất cần có 2 tháng dữ liệu để có thể dự đoán một cách hợp lý
            if len(savings) >= 2:
                y = savings  # Sử dụng dữ liệu tiết kiệm lịch sử thực tế

                # Tạo một ARIMA model để dự đoán 4 tháng tiếp theo
                try:
                    model = ARIMA(
                        y, order=(1, 1, 1)
                    )  # (p, d, q) có thể thay đổi tùy thuộc vào mức độ phù hợp với dữ liệu
                    model_fit = model.fit()  # Huấn luyện mô hình

                    # Kiểm tra dự báo có hợp lệ hay không
                    if len(y) > 0:
                        predicted_values = model_fit.forecast(
                            steps=4
                        )  # Dự đoán cho 4 tháng tiếp theo
                        # Tổng các giá trị dự đoán để có tổng tiết kiệm trong 4 tháng tiếp theo
                        predicted_savings[shop_title] = round(
                            max(0, float(np.sum(predicted_values))), 2
                        )
                    else:
                        predicted_savings[shop_title] = 0
                except Exception as e:
                    # Thông báo lỗi nếu mô hình không thể dự đoán được
                    print(f"Không thể dự đoán cho cửa hàng {shop_title} do lỗi: {e}")
                    predicted_savings[shop_title] = 0
            else:
                # Nếu có ít hơn 2 tháng dữ liệu, đặt giá trị dự đoán là 0
                print(f"Không đủ dữ liệu để dự đoán cho cửa hàng {shop_title}")
                predicted_savings[shop_title] = 0

        return predicted_savings

    def generate_chart_config(self, title: str, data: Dict[str, float]):
        """
        Tạo cấu hình biểu đồ Pie Chart.

        Parameters:
        - title (str): Tiêu đề của biểu đồ.
        - data (Dict[str, float]): Dữ liệu cần biểu diễn trên biểu đồ.

        Returns:
        - dict: Cấu hình biểu đồ.
        """
        # Chuẩn bị dữ liệu cho biểu đồ pie chart
        series_data = [{"name": shop, "y": savings} for shop, savings in data.items()]

        # Tạo cấu hình cho biểu đồ Pie Chart
        chart_config = {
            "chart": {
                "type": "pie",
                "style": {
                    "fontFamily": "MyCustomFont"
                },  # Sử dụng font tùy chỉnh cho toàn bộ biểu đồ
            },
            "title": {
                "text": title,
                "style": {
                    "fontFamily": "MyCustomFont"
                },  # Sử dụng font tùy chỉnh cho tiêu đề
            },
            "tooltip": {
                "pointFormat": "<b>{point.percentage:.1f}%</b> của tổng số tiền tiết kiệm"
            },
            "plotOptions": {
                "pie": {
                    "allowPointSelect": True,
                    "cursor": "pointer",
                    "dataLabels": {
                        "enabled": True,
                        "format": "<b>{point.name}</b>: {point.percentage:.1f} %",
                    },
                    "showInLegend": True,  # Hiển thị dữ liệu trong legend
                }
            },
            "legend": {
                "align": "center",  # Căn giữa legend
                "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
                "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
                "itemDistance": 50,  # Khoảng cách giữa các mục trong legend
                "padding": 20,  # Khoảng cách giữa legend và biểu đồ
                "itemStyle": {
                    "fontSize": "14px",  # Kích thước chữ trong legend
                    "fontWeight": "bold",  # Để chữ đậm
                    "color": "black",  # Màu chữ trong legend
                },
            },
            "series": [
                {
                    "name": "Tổng số tiền tiết kiệm",
                    "colorByPoint": True,
                    "data": series_data,
                }
            ],
        }

        return chart_config

    def generate_js(self, output_file="price_chart_pie.js"):
        """
        Tạo file js cho biểu đồ Pie Chart.

        Parameters:
        - output_file (str): Tên của file js đầu ra, mặc định là 'discount_savings_pie_chart.js'.
        """
        # Tách riêng dữ liệu tổng tiết kiệm và dữ liệu tiết kiệm hàng tháng
        total_savings, monthly_savings = (
            self.process_raw_data()
        )  # Tách thành 2 biến riêng biệt

        # Tạo cấu hình cho biểu đồ dựa trên tổng số tiền tiết kiệm
        historical_chart_config = self.generate_chart_config(
            "Tổng số tiền tiết kiệm từ giảm giá theo cửa hàng (Lịch sử)",
            total_savings,  # Chỉ truyền vào total_savings
        )
        historical_chart_json = json.dumps(historical_chart_config)

        # Dự đoán dữ liệu tiết kiệm cho 4 tháng tiếp theo
        predicted_data = self.predict_next_four_months(
            monthly_savings
        )  # Sử dụng monthly_savings

        # Tạo cấu hình cho biểu đồ dựa trên dữ liệu dự đoán
        predicted_chart_config = self.generate_chart_config(
            "Dự đoán tổng số tiền tiết kiệm từ giảm giá theo cửa hàng (4 tháng tiếp theo)",
            predicted_data,
        )
        predicted_chart_json = json.dumps(predicted_chart_config)

        # Js for two charts side by side
        script_content = textwrap.dedent(
            """
                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {};
                    var chartConfig2 = {};

                    Highcharts.chart('container1', chartConfig1);
                    Highcharts.chart('container2', chartConfig2);
                }});
        """.format(
                historical_chart_json,
                predicted_chart_json,
            )
        )

        # Ghi file js ra output
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(script_content)

        print(f"Biểu đồ đã được lưu vào {output_file}")


# Sử dụng GameDealFetcher và DiscountSavingsPieChart để tạo biểu đồ Pie Chart
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "PriceChart/shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo DiscountSavingsPieChart để tạo biểu đồ Pie Chart
    pie_chart = DiscountSavingsPieChart(formatted_data)
    pie_chart.generate_js(
        "PriceChart/PieChart/price_chart_pie.js"
    )  # Tạo file js cho biểu đồ Pie Chart


if __name__ == "__main__":
    main()
