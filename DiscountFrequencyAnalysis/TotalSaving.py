import json
import requests
import datetime
from typing import Dict, List, Union
from collections import defaultdict
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# Class GameDealFetcher để lấy dữ liệu từ API
class GameDealFetcher:
    def __init__(
        self,
        api_key: str,               # api_key: Mã khóa API để truy cập dịch vụ.
        game_id: str,               # game_id: ID của trò chơi cần lấy dữ liệu giảm giá.
        shops_file: str,            # shops_file: Đường dẫn tới file JSON chứa dữ liệu các cửa hàng.
        country: str = "US",        # country: Mã quốc gia, mặc định là "US".
        shops: str = "61,35,16,6,20,24,37",  # shops: Danh sách các ID cửa hàng muốn lấy dữ liệu.
        since: str = "2023-11-06T00:00:00Z",  # since: Thời gian bắt đầu lấy dữ liệu.
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
        Hàm này dùng để đọc dữ liệu các cửa hàng từ file JSON.
        
        Parameters:
        - shops_file: Đường dẫn tới file JSON chứa dữ liệu các cửa hàng.
        
        Returns:
        - Một dictionary chứa dữ liệu các cửa hàng.
        """
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        """
        Hàm này gửi yêu cầu HTTP tới API để lấy lịch sử giảm giá của trò chơi.
        
        Parameters:
        - Không có tham số đầu vào.
        
        Returns:
        - Một danh sách hoặc dictionary chứa dữ liệu lịch sử giảm giá từ API.
        
        Lưu ý:
        - Nếu có lỗi xảy ra trong quá trình gửi yêu cầu, hàm sẽ ném ra ngoại lệ.
        """
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        """
        Hàm này định dạng lại dữ liệu trả về từ API để dễ dàng xử lý và hiển thị.
        
        Parameters:
        - data: Dữ liệu trả về từ API (dạng danh sách hoặc dictionary).
        
        Returns:
        - Một danh sách các dictionary chứa thông tin giao dịch của các cửa hàng.
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


# Class TotalSavingsColumnChart để tạo biểu đồ Column Chart
class TotalSavingsColumnChart:
    def __init__(self, shops_data: List[Dict]):
        """
        Khởi tạo đối tượng để tạo biểu đồ cột về tổng tiết kiệm của các cửa hàng.
        
        Parameters:
        - shops_data: Dữ liệu của các cửa hàng và thông tin giao dịch giảm giá từ API.
        """
        self.shops_data = shops_data

    def process_raw_data(self) -> Dict[str, float]:
        """
        Tính tổng số tiền tiết kiệm được cho mỗi cửa hàng từ dữ liệu giảm giá.
        
        Parameters:
        - Không có tham số đầu vào.
        
        Returns:
        - Một dictionary với tên cửa hàng là key và tổng số tiền tiết kiệm (USD) là value.
        """
        total_savings = defaultdict(float)

        # Tính toán tiết kiệm cho mỗi giao dịch và cộng dồn theo cửa hàng
        for shop in self.shops_data:
            shop_title = shop["shop_title"]

            for deal in shop["deals"]:
                regular_price = deal["regular_price"]
                discounted_price = deal["price"]
                savings = regular_price - discounted_price

                if savings > 0:
                    total_savings[shop_title] += savings

        total_savings = {k: round(v, 2) for k, v in total_savings.items()}
        return total_savings

    def predict_next_twelve_months(
        self, historical_data: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Dự đoán tổng số tiền tiết kiệm của mỗi cửa hàng trong 12 tháng tiếp theo bằng phương pháp Exponential Smoothing.
        
        Parameters:
        - historical_data: Dữ liệu lịch sử về tiết kiệm của các cửa hàng.
        
        Returns:
        - Một dictionary chứa dữ liệu dự đoán tổng tiết kiệm của các cửa hàng trong 12 tháng tới.
        """
        predicted_savings = {}

        # Dự đoán tiết kiệm trong tương lai cho mỗi cửa hàng
        for shop_title, total_savings in historical_data.items():
            if total_savings > 0:
                # Giả sử có dữ liệu lịch sử 12 tháng
                historical_values = [total_savings / 12] * 12

                # Sử dụng Exponential Smoothing để dự đoán
                model = ExponentialSmoothing(
                    historical_values, trend="add", seasonal=None
                ).fit()
                forecast = model.forecast(12)

                # Tính tổng số tiền tiết kiệm dự đoán cho cả năm
                predicted_savings[shop_title] = round(max(0, float(np.sum(forecast))),2)
            else:
                predicted_savings[shop_title] = 0

        return predicted_savings

    def generate_chart_config(self, title: str, data: Dict[str, float]):
        """
        Tạo cấu hình cho biểu đồ cột.
        
        Parameters:
        - title: Tiêu đề của biểu đồ.
        - data: Dữ liệu cho biểu đồ, với các cửa hàng là key và tổng tiết kiệm là value.
        
        Returns:
        - Cấu hình cho biểu đồ cột.
        """
        categories = list(data.keys())
        values = list(data.values())

        chart_config = {
            "chart": {"type": "column", "style": {"fontFamily": "MyCustomFont"}},
            "title": {"text": title, "style": {"fontFamily": "MyCustomFont"}},
            "xAxis": {"categories": categories, "title": {"text": "Cửa hàng"}},
            "yAxis": {"title": {"text": "Tổng tiết kiệm (USD)"}},
            "series": [{"name": "Tổng tiết kiệm", "data": values}],
        }

        return chart_config

    def generate_html(self, output_file="total_savings_chart.html"):
        """
        Hàm này tạo file HTML chứa hai biểu đồ: một biểu đồ lịch sử và một biểu đồ dự đoán.
        
        Parameters:
        - output_file: Tên file HTML xuất ra (mặc định là "total_savings_chart.html").
        
        Returns:
        - Không có giá trị trả về. Hàm sẽ tạo và lưu file HTML.
        """
        # Xử lý dữ liệu lịch sử để có tổng tiết kiệm của mỗi cửa hàng
        historical_data = self.process_raw_data()

        # Tạo cấu hình biểu đồ cho dữ liệu lịch sử
        historical_chart_config = self.generate_chart_config(
            "Tổng tiết kiệm từ giảm giá cho mỗi cửa hàng (Lịch sử)", historical_data
        )
        historical_chart_json = json.dumps(historical_chart_config)

        # Dự đoán dữ liệu cho 12 tháng tới và tạo biểu đồ cho dữ liệu dự đoán
        predicted_data = self.predict_next_twelve_months(historical_data)
        predicted_chart_config = self.generate_chart_config(
            "Dự đoán tổng tiết kiệm từ giảm giá cho mỗi cửa hàng (12 tháng tới)",
            predicted_data,
        )
        predicted_chart_json = json.dumps(predicted_chart_config)

        # HTML Template 
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Biểu đồ cột - Tổng tiết kiệm với dự đoán</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
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
                    var chartConfig1 = {historical_chart_json};
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

        print(f"Biểu đồ đã được lưu vào {output_file}")


# Sử dụng GameDealFetcher và TotalSavingsColumnChart để tạo biểu đồ Column Chart
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo TotalSavingsColumnChart để tạo biểu đồ
    column_chart = TotalSavingsColumnChart(formatted_data)
    column_chart.generate_html(
        "total_savings_chart.html"
    )  # Tạo file HTML với biểu đồ Column Chart


if __name__ == "__main__":
    main()
