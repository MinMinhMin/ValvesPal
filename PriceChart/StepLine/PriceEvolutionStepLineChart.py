import json
import math
import textwrap
import requests
import datetime
from typing import Dict, List, Union
import pandas as pd
import numpy as np
from datetime import datetime


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

        full_date_range = pd.date_range(
            start=min_date, end=max_date, freq="D", tz="UTC"
        )

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

            # Reindex lại dataframe để bao gồm tất cả các ngày, điền giá trị thiếu bằng phương pháp forward fill
            df = df.reindex(full_date_range, method="ffill")

            # Dự đoán giá trong tương lai (120 ngày tiếp theo) bằng chu kỳ trung bình
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

    def getCycle(flags):
        n = len(flags)
        false_lengths = []
        i = 0

        while i < n:
            if not flags[i]:  # Start of a False subarray
                start = i
                while i < n and not flags[i]:
                    i += 1
                end = i - 1
                # Add the length of this False subarray
                false_lengths.append(end - start + 1)
            else:
                i += 1

        # Calculate the average length of False subarrays
        if false_lengths:
            average_length = sum(false_lengths) / len(false_lengths)
        else:
            average_length = 0

        return int(average_length)

    def getPredictions(prices: np.ndarray, periods: int):
        if len(prices) == 0:
            return []
        min_price = np.nanmin(prices)
        max_price = np.nanmax(prices)

        print(f"Min price: {min_price} - Max price: {max_price}")

        cpoint = []
        cycle_min = 0
        count_cycle_min = 0
        predicts = []
        last_min = 0

        n = len(prices)
        flags = [False] * n  # Initialize all as False

        t = 0
        while t < n:
            # Find the start of a group of identical elements
            if prices[t] == np.nan:
                continue
            start = t
            while t + 1 < n and prices[t] == prices[t + 1]:
                t += 1
            end = t

            # Check valley conditions
            if (start > 0 and prices[start] < prices[start - 1]) and (
                end < n - 1 and prices[end] < prices[end + 1]
            ):
                for j in range(start, end + 1):
                    flags[j] = True

            # Move to the next group
            t += 1

        cycle = PriceEvolutionLineChart.getCycle(flags)

        print(cycle)

        x = 1000000000
        y = -1
        for i in range(0, len(prices)):
            # print(min)
            if flags[i] == True:
                last_min = i
                x = min(x, i)
                y = max(y, i)
            else:
                if y != -1:
                    cpoint.append(x)
                    cpoint.append(y)
                x = 1000000000
                y = -1
        if y != -1:
            cpoint.append(x)
            cpoint.append(y)

        for i in range(0, len(cpoint)):
            if i % 2 == 1:
                count_cycle_min += 1
                cycle_min += cpoint[i] - cpoint[i - 1]
        if count_cycle_min != 0:
            cycle_min = cycle_min // count_cycle_min
        else:
            cycle_min = cycle
        if len(prices) - last_min < cycle:
            for i in range(0, cycle - (len(prices) - last_min)):
                predicts.append(prices[-1])
                if len(predicts) == periods:
                    return predicts
        if prices[-1] != min_price:
            for i in range(0, cycle_min):
                predicts.append(min_price)
                if len(predicts) == periods:
                    return predicts

        while len(predicts) < periods:
            for i in range(0, cycle):
                predicts.append(max_price)
                if len(predicts) == periods:
                    return predicts
            l_p = -1
            for i in range(0, cycle_min):

                predicts.append(min_price)
                if len(cpoint) != 0:
                    l_p = cpoint[-1] + i + 1
                if len(predicts) == periods:

                    return predicts
            if l_p != -1:
                cpoint.append(l_p)
                sum = 0
                c = 0
                for j in range(0, len(cpoint)):
                    if j % 2 == 1:
                        sum += cpoint[j] - cpoint[j - 1]
                        c += 1
                cycle_min = sum // c
        return predicts

    def forecast_prices(self, df, periods=120):

        # # Create a pandas series for the forecast with the proper index (dates)
        future_dates = pd.date_range(
            start=df.index[-1] + pd.Timedelta(days=1), periods=periods, freq="D"
        )
        # print(df)
        forecast_series = pd.Series(
            PriceEvolutionLineChart.getPredictions(df["price"].to_numpy(), periods),
            index=future_dates,
        )
        # print(forecast_series.round(2))

        return forecast_series.round(2)

    def generate_js(
        self,
        output_file: str = "output/price_chart_step_line.js",
    ):

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
                    "dateTimeLabelFormats": {
                        "day": "%e %b %Y"
                    },  # Định dạng ngày tháng trong tooltip
                    "style": {
                        "fontFamily": "'MyCustomFont', sans-serif",  # Phông chữ của tooltip
                        "fontSize": "10px",  # Kích thước phông chữ của tooltip
                    },
                },
                "series": [
                    series_data[i],
                    series_data[i + 1],
                    series_data[i + 2],
                ],  # Các chuỗi thực tế, nối và dự báo
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

            script_content = textwrap.dedent(
                """
            function AddContainer() {{
                const body = document.getElementById('main');


                const n = {}; // Replace this with the desired number of containers

                for (let i = 0; i < n; i++) {{
                    const div = document.createElement('div');

                    div.id = `container-${{i}}`;
                    div.style.width = '100%';
                    div.style.height = '400px';
                    div.style.margin = '20px 0';
                    div.textContent = `This is container ${{i}}`; // Optional: add text content

                    body.appendChild(div);
                }}
            }}
    """.format(
                    len(chart_configs)
                )
            )

            script_content += textwrap.dedent(
                """
                AddContainer();
                let charts = [];

                document.addEventListener('DOMContentLoaded', function () {

            """
            )

            for i, config in enumerate(chart_configs):
                script_content += textwrap.dedent(
                    f"""
                const config_{i} = {json.dumps(config)};
                const chart_{i} = Highcharts.chart('container-{i}', config_{i});
                charts.push(chart_{i});
                """
                )

            script_content += textwrap.dedent(
                """
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
"""
            )
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(script_content)
            print(f"File Js đã được tạo thành công: {output_file}")
        except Exception as e:
            print(f"Lỗi khi tạo file Js: {str(e)}")


def main():
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937e-fde4-72ff-a7af-45e4955a8dd6"
    shops_file = "PriceChart/shops.json"

    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    price_evolution_chart = PriceEvolutionLineChart(formatted_data)
    price_evolution_chart.generate_js("PriceChart/StepLine/price_chart_step_line.js")


if __name__ == "__main__":
    main()
