import json
from typing import List
from PriceChart.BoxPlot.MaxAndMinDiscountAnalysis import (
    GameDealFetcher,
    MaximumMinimumDiscountBoxPlot,
)  # File Python thứ nhất chứa class này
from PriceChart.ColumnChart.TotalSaving import (
    TotalSavingsColumnChart,
)  # File Python thứ hai chứa class này
from PriceChart.GroupBar.PriceComparisonGrouped import (
    PriceComparisonGroupedBarChart,
)  # File Python thứ ba chứa class này
from PriceChart.HeatMap.DiscountFrequencyAnalysis import (
    DiscountFrequencyHeatmap,
)  # File Python thứ tư chứa class này
from PriceChart.PieChart.DiscountSaving import (
    DiscountSavingsPieChart,
)  # File Python thứ năm chứa class này
from PriceChart.StepLine.PriceEvolutionStepLineChart import (
    PriceEvolutionLineChart,
)  # File Python thứ sáu chứa class này


def generate_multiple_html_files(api_key: str, game_ids: List[str], shops_file: str):

    for index, game_id in enumerate(game_ids):
        try:
            # Khởi tạo GameDealFetcher để lấy dữ liệu từ API cho mỗi game_id
            fetcher = GameDealFetcher(api_key, game_id, shops_file)
            raw_data = fetcher.fetch_deal_history()
            formatted_data = fetcher.format_data(raw_data)

            box_plot_chart = MaximumMinimumDiscountBoxPlot([])
            box_plot_chart.process_raw_data(formatted_data)
            box_plot_chart.generate_js("PriceChart/BoxPlot/price_chart_boxplot.js")

            print(
                "File HTML Box Plot đã được tạo thành công: PriceChart/BoxPlot/price_chart_boxplot.js"
            )

            grouped_bar_chart = PriceComparisonGroupedBarChart(formatted_data)
            grouped_bar_chart.generate_js(
                "PriceChart/GroupBar/price_chart_grouped_bar.js"
            )

            print(
                "File HTML Grouped Bar Chart đã được tạo thành công: PriceChart/GroupBar/price_chart_grouped_bar.js"
            )

            step_line_chart = PriceEvolutionLineChart(formatted_data)
            step_line_chart.generate_js("PriceChart/StepLine/price_chart_step_line.js")

            print(
                "File HTML Step Line Chart đã được tạo thành công: PriceChart/StepLine/price_chart_step_line.js"
            )

            heatmap_chart = DiscountFrequencyHeatmap(formatted_data)
            heatmap_chart.generate_js("PriceChart/HeatMap/price_chart_heatmap.js")

            print(
                "File HTML Heatmap đã được tạo thành công: PriceChart/HeatMap/price_chart_heatmap.js"
            )

            column_chart = TotalSavingsColumnChart(formatted_data)
            column_chart.generate_js("PriceChart/ColumnChart/price_chart_column.js")

            print(
                "File HTML Column Chart đã được tạo thành công: PriceChart/ColumnChart/price_chart_column.js"
            )

            pie_chart = DiscountSavingsPieChart(formatted_data)
            pie_chart.generate_js("PriceChart/PieChart/price_chart_pie.js")

            print(
                "File HTML Pie Chart đã được tạo thành công: PriceChart/PieChart/price_chart_pie.js"
            )

            return True

        except Exception as e:
            print(f"Lỗi khi xử lý game ID {game_id}: {str(e)}")
            return False


def visualize_PriceChart(id):
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    shops_file = "PriceChart/shops.json"

    # Danh sách game IDs (giả định rằng bạn có 6 game IDs khác nhau để sử dụng)
    game_ids = [
        id,
    ]

    # Gọi hàm để tạo các file HTML
    if generate_multiple_html_files(api_key, game_ids, shops_file):
        return True

    return False


# visualize_PriceChart("018d937e-fcfb-7291-bf00-f651841d24d4")
