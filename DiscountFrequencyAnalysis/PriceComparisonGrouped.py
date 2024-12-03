import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import json
import requests
from datetime import datetime
from typing import Dict, List, Union
from collections import defaultdict

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
        """
        Khởi tạo đối tượng GameDealFetcher với các tham số cấu hình để lấy dữ liệu từ API.

        :param api_key: Khóa API để truy cập vào dịch vụ.
        :param game_id: ID của trò chơi cần lấy dữ liệu.
        :param shops_file: Đường dẫn tới tệp JSON chứa thông tin các cửa hàng.
        :param country: Quốc gia mà người dùng muốn lấy dữ liệu, mặc định là "US".
        :param shops: Danh sách các cửa hàng mà người dùng muốn lấy thông tin, mặc định là "61,35,16,6,20,24,37".
        :param since: Thời gian bắt đầu để lấy dữ liệu, mặc định là "2023-11-06T00:00:00Z".
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
        Tải dữ liệu cửa hàng từ tệp JSON.

        :param shops_file: Đường dẫn tới tệp JSON chứa thông tin các cửa hàng.
        :return: Dữ liệu cửa hàng dưới dạng từ điển.
        """
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc tệp JSON cửa hàng: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        """
        Lấy lịch sử giảm giá từ API.

        :return: Dữ liệu lịch sử giảm giá (dạng danh sách hoặc từ điển).
        """
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Lỗi: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict, str]) -> List[Dict]:
        """
        Định dạng dữ liệu từ API thành cấu trúc có tổ chức hơn để dễ xử lý.

        :param data: Dữ liệu từ API trả về (dạng danh sách, từ điển, hoặc chuỗi JSON).
        :return: Dữ liệu đã được định dạng dưới dạng danh sách các từ điển.
        """
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        formatted_data = []

        for item in data:
            shop_id = str(item["shop"]["id"])
            shop_name = self.shops_data.get(shop_id, "Cửa hàng không xác định")
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


# Class PriceComparisonGroupedBarChart để tạo biểu đồ cột nhóm
class PriceComparisonGroupedBarChart:
    def __init__(self, shops_data: List[Dict]):
        """
        Khởi tạo đối tượng PriceComparisonGroupedBarChart với dữ liệu các cửa hàng.

        :param shops_data: Dữ liệu các cửa hàng đã được định dạng.
        """
        self.shops_data = shops_data

    def process_raw_data(self) -> List[Dict]:
        """
        Xử lý dữ liệu thô để tạo dữ liệu cho biểu đồ cột nhóm, tính giá trị lớn nhất, nhỏ nhất và trung bình.
        """
        # Khởi tạo danh sách chứa tất cả các tháng có trong dữ liệu
        all_dates = set()
        for shop in self.shops_data:
            for deal in shop["deals"]:
                date = deal["timestamp"].split("T")[0][:7]
                all_dates.add(date)

        all_dates = (
            pd.date_range(start=min(all_dates), end=max(all_dates), freq="MS")
            .strftime("%Y-%m")
            .tolist()
        )

        time_point_data = defaultdict(dict)
        latest_prices = {}  # Lưu giá mới nhất của từng shop

        for date in all_dates:
            for shop in self.shops_data:
                shop_title = shop["shop_title"]

                # Lọc những deal có ngày nhỏ hơn hoặc bằng tháng hiện tại
                relevant_deals = [
                    deal
                    for deal in shop["deals"]
                    if deal["timestamp"].split("T")[0][:7] <= date
                ]

                if relevant_deals:
                    # Lấy giá trị lớn nhất và nhỏ nhất của shop trong tháng đó
                    max_deal = max(relevant_deals, key=lambda x: x["price"])
                    min_deal = min(relevant_deals, key=lambda x: x["price"])
                    avg_price = (max_deal["price"] + min_deal["price"]) / 2
                    time_point_data[date][f"{shop_title}_max"] = max_deal["price"]
                    time_point_data[date][f"{shop_title}_min"] = min_deal["price"]
                    time_point_data[date][f"{shop_title}_avg"] = avg_price
                    latest_prices[shop_title] = {"max": max_deal["price"], "min": min_deal["price"], "avg": avg_price}
                else:
                    # Nếu không có deal, lấy giá trị mới nhất đã biết
                    if shop_title in latest_prices:
                        time_point_data[date][f"{shop_title}_max"] = latest_prices[shop_title]["max"]
                        time_point_data[date][f"{shop_title}_min"] = latest_prices[shop_title]["min"]
                        time_point_data[date][f"{shop_title}_avg"] = latest_prices[shop_title]["avg"]
                    else:
                        # Nếu chưa từng có deal, để giá là 0
                        time_point_data[date][f"{shop_title}_max"] = 0
                        time_point_data[date][f"{shop_title}_min"] = 0
                        time_point_data[date][f"{shop_title}_avg"] = 0

        formatted_data = []
        for date, prices in time_point_data.items():
            formatted_data.append({"time_point": date, "prices": prices})

        return formatted_data


    def predict_next_twelve_months(self, processed_data: List[Dict]) -> List[Dict]:
        """
        Dự đoán giá trong 12 tháng tiếp theo dựa trên dữ liệu đã xử lý, sử dụng mô hình ARIMA.
        """
        all_dates = pd.to_datetime([entry["time_point"] for entry in processed_data])
        next_twelve_months = [
            (all_dates[-1] + pd.DateOffset(months=i)).strftime("%Y-%m")
            for i in range(1, 13)
        ]

        shop_names = sorted(
            {shop.split("_")[0] for entry in processed_data for shop in entry["prices"].keys()}
        )
        
        predictions = []

        for shop_name in shop_names:
            # Lấy dữ liệu giá trị cho shop
            shop_prices_max = [
                entry["prices"].get(f"{shop_name}_max", None) for entry in processed_data
            ]
            shop_prices_min = [
                entry["prices"].get(f"{shop_name}_min", None) for entry in processed_data
            ]
            shop_prices_avg = [
                entry["prices"].get(f"{shop_name}_avg", None) for entry in processed_data
            ]

            if len(shop_prices_max) > 1:
                # Chuyển dữ liệu thành dạng mảng numpy để sử dụng trong ARIMA
                max_values = np.array([x for x in shop_prices_max if x is not None])
                min_values = np.array([x for x in shop_prices_min if x is not None])
                avg_values = np.array([x for x in shop_prices_avg if x is not None])

                # Dự đoán giá trị max, min và avg với ARIMA
                try:
                    model_max = ARIMA(max_values, order=(1, 1, 1))  # ARIMA(p,d,q), p, d, q có thể thử các giá trị khác
                    model_min = ARIMA(min_values, order=(1, 1, 1))
                    model_avg = ARIMA(avg_values, order=(1, 1, 1))

                    # Huấn luyện mô hình
                    model_max_fit = model_max.fit()
                    model_min_fit = model_min.fit()
                    model_avg_fit = model_avg.fit()

                    # Dự đoán cho 12 tháng tới
                    forecast_max = model_max_fit.forecast(steps=12)
                    forecast_min = model_min_fit.forecast(steps=12)
                    forecast_avg = model_avg_fit.forecast(steps=12)

                    # Lưu kết quả dự đoán
                    for i, date in enumerate(next_twelve_months):
                        predictions.append({
                            "time_point": date,
                            "shop_name": shop_name,
                            "predicted_max_price": round(max(0, float(forecast_max[i])), 2),
                            "predicted_min_price": round(max(0, float(forecast_min[i])), 2),
                            "predicted_avg_price": round(max(0, float(forecast_avg[i])), 2)
                        })
                except Exception as e:
                    print(f"Error with ARIMA prediction for {shop_name}: {e}")
                    continue

        # Chuyển dữ liệu dự đoán thành cấu trúc phù hợp với biểu đồ
        formatted_predictions = defaultdict(dict)
        for prediction in predictions:
            formatted_predictions[prediction["time_point"]][f"{prediction['shop_name']}_max"] = prediction["predicted_max_price"]
            formatted_predictions[prediction["time_point"]][f"{prediction['shop_name']}_min"] = prediction["predicted_min_price"]
            formatted_predictions[prediction["time_point"]][f"{prediction['shop_name']}_avg"] = prediction["predicted_avg_price"]

        formatted_data = [
            {"time_point": date, "prices": formatted_predictions[date]}
            for date in next_twelve_months
        ]
        
        # Debugging: In dữ liệu dự đoán để kiểm tra
        print("Dữ liệu dự đoán:", formatted_data)

        return formatted_data

    def generate_chart_config(self):
        """
        Tạo cấu hình cho ba biểu đồ cột nhóm: một cho giá trị lớn nhất, một cho giá trị nhỏ nhất và một cho giá trị trung bình.
        """
        processed_data = self.process_raw_data()

        # Dữ liệu gốc cho Biểu đồ cột nhóm
        time_points = [entry["time_point"] for entry in processed_data]
        shop_names = sorted(
            {shop.split("_")[0] for entry in processed_data for shop in entry["prices"].keys()}
        )

        # Series cho giá trị lớn nhất, nhỏ nhất và trung bình
        max_series = []
        min_series = []
        avg_series = []

        for shop_name in shop_names:
            max_prices = [
                entry["prices"].get(f"{shop_name}_max", None) for entry in processed_data
            ]
            min_prices = [
                entry["prices"].get(f"{shop_name}_min", None) for entry in processed_data
            ]
            avg_prices = [
                entry["prices"].get(f"{shop_name}_avg", None) for entry in processed_data
            ]

            max_series.append({"name": f"{shop_name}_max", "data": max_prices})
            min_series.append({"name": f"{shop_name}_min", "data": min_prices})
            avg_series.append({"name": f"{shop_name}_avg", "data": avg_prices})

        # Biểu đồ giá trị lớn nhất
        original_max_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "So sánh giá trị lớn nhất cho mỗi cửa hàng (Hàng tháng)",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
            "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": max_series,
        }

        # Biểu đồ giá trị nhỏ nhất
        original_min_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "So sánh giá trị nhỏ nhất cho mỗi cửa hàng (Hàng tháng)",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
             "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": min_series,
        }

        # Biểu đồ giá trị trung bình
        original_avg_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "So sánh giá trị trung bình cho mỗi cửa hàng (Hàng tháng)",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
             "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": avg_series,
        }

        # Dự đoán cho 12 tháng tiếp theo
        predicted_data = self.predict_next_twelve_months(processed_data)
        predicted_time_points = [entry["time_point"] for entry in predicted_data]
        
        # Series cho dự đoán giá trị lớn nhất, nhỏ nhất và trung bình
        predicted_max_series = []
        predicted_min_series = []
        predicted_avg_series = []

        for shop_name in shop_names:
            predicted_max_prices = [
                entry["prices"].get(f"{shop_name}_max", None) for entry in predicted_data
            ]
            predicted_min_prices = [
                entry["prices"].get(f"{shop_name}_min", None) for entry in predicted_data
            ]
            predicted_avg_prices = [
                entry["prices"].get(f"{shop_name}_avg", None) for entry in predicted_data
            ]

            predicted_max_series.append({"name": f"{shop_name}_max", "data": predicted_max_prices})
            predicted_min_series.append({"name": f"{shop_name}_min", "data": predicted_min_prices})
            predicted_avg_series.append({"name": f"{shop_name}_avg", "data": predicted_avg_prices})

        # Biểu đồ dự đoán giá trị lớn nhất
        prediction_max_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "Dự đoán giá trị lớn nhất cho 12 tháng tiếp theo",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": predicted_time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
             "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": predicted_max_series,
        }

        # Biểu đồ dự đoán giá trị nhỏ nhất
        prediction_min_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "Dự đoán giá trị nhỏ nhất cho 12 tháng tiếp theo",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": predicted_time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
             "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": predicted_min_series,
        }

        # Biểu đồ dự đoán giá trị trung bình
        prediction_avg_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "Dự đoán giá trị trung bình cho 12 tháng tiếp theo",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": predicted_time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
             "legend": {
            "align": "center",  # Căn giữa legend
            "verticalAlign": "bottom",  # Đặt legend dưới biểu đồ
            "layout": "horizontal",  # Sắp xếp các mục trong legend theo chiều ngang
            "itemDistance": 65,  # Khoảng cách giữa các mục trong legend
            "padding": 20,  # Khoảng cách giữa legend và biểu đồ
            "itemStyle": {
                "fontSize": "14px",  # Kích thước chữ trong legend
                "fontWeight": None,  # Để chữ đậm
                "color": "black"  # Màu chữ trong legend
            },
        },
            "series": predicted_avg_series,
        }

        return (
            original_max_chart_config,
            original_min_chart_config,
            original_avg_chart_config,
            prediction_max_chart_config,
            prediction_min_chart_config,
            prediction_avg_chart_config,
        )

    def generate_html(self, output_file="grouped_bar_chart.html"):
        """
        Tạo và lưu file HTML với ba biểu đồ cột nhóm (giá trị lớn nhất, nhỏ nhất và trung bình).
        """
        original_max_chart_config, original_min_chart_config, original_avg_chart_config, \
        prediction_max_chart_config, prediction_min_chart_config, prediction_avg_chart_config = self.generate_chart_config()

        original_max_chart_json = json.dumps(original_max_chart_config)
        original_min_chart_json = json.dumps(original_min_chart_config)
        original_avg_chart_json = json.dumps(original_avg_chart_config)
        prediction_max_chart_json = json.dumps(prediction_max_chart_config)
        prediction_min_chart_json = json.dumps(prediction_min_chart_config)
        prediction_avg_chart_json = json.dumps(prediction_avg_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Biểu đồ cột nhóm - So sánh giá với dự đoán</title>
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
            <div id="container2" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container3" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container4" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container5" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container6" style="width: 100%; height: 500px;"></div>
            <script type="text/javascript">
                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {original_max_chart_json};
                    var chartConfig2 = {original_min_chart_json};
                    var chartConfig3 = {original_avg_chart_json};
                    var chartConfig4 = {prediction_max_chart_json};
                    var chartConfig5 = {prediction_min_chart_json};
                    var chartConfig6 = {prediction_avg_chart_json};

                    Highcharts.chart('container1', chartConfig1);
                    Highcharts.chart('container2', chartConfig2);
                    Highcharts.chart('container3', chartConfig3);
                    Highcharts.chart('container4', chartConfig4);
                    Highcharts.chart('container5', chartConfig5);
                    Highcharts.chart('container6', chartConfig6);
                }});
            </script>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_template)

        print(f"Biểu đồ đã được lưu vào {output_file}")




# Use GameDealFetcher and PriceComparisonGroupedBarChart to generate the chart
def main():
    # Necessary Information
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Initialize GameDealFetcher to fetch data from API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Initialize PriceComparisonGroupedBarChart to generate chart
    grouped_bar_chart = PriceComparisonGroupedBarChart(formatted_data)
    grouped_bar_chart.generate_html(
        "grouped_bar_chart.html"
    )  # Create HTML file with Grouped Bar Chart


if __name__ == "__main__":
    main()