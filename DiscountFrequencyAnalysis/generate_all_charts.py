import json
from typing import List
from DiscountFrequencyAnalysis.MaxAndMinDiscountAnalysis import (
    GameDealFetcher,
    MaximumMinimumDiscountBoxPlot,
)  
from DiscountFrequencyAnalysis.PriceComparisonGrouped import (
    PriceComparisonGroupedBarChart,
)  
from DiscountFrequencyAnalysis.PriceEvolutionStepLineChart import (
    PriceEvolutionLineChart,
)  
from DiscountFrequencyAnalysis.DiscountFrequencyAnalysis import (
    DiscountFrequencyHeatmap,
)  
from DiscountFrequencyAnalysis.TotalSaving import (
    TotalSavingsColumnChart,
)  
from DiscountFrequencyAnalysis.DiscountSaving import (
    DiscountSavingsPieChart,
)  

def generate_multiple_html_files(
    api_key: str, game_ids: List[str], shops_file: str, output_filenames: List[str]
):
    if len(game_ids) != len(output_filenames):
        raise ValueError(
            "The number of game_ids must match the number of output filenames"
        )

    for index, game_id in enumerate(game_ids):
        try:
            # Khởi tạo GameDealFetcher để lấy dữ liệu từ API cho mỗi game_id
            fetcher = GameDealFetcher(api_key, game_id, shops_file)
            raw_data = fetcher.fetch_deal_history()
            formatted_data = fetcher.format_data(raw_data)

            # Tạo biểu đồ Box Plot và lưu dưới dạng HTML
            box_plot_output_file = "DiscountFrequencyAnalysis/"+output_filenames[index] + "_boxplot.html"
            box_plot_chart = MaximumMinimumDiscountBoxPlot([])
            box_plot_chart.process_raw_data(formatted_data)
            box_plot_chart.generate_html(box_plot_output_file)

            print(f"File HTML Box Plot đã được tạo thành công: {box_plot_output_file}")

            # Tạo biểu đồ Grouped Bar Chart  dưới dạng HTML
            grouped_bar_output_file = "DiscountFrequencyAnalysis/"+output_filenames[index] + "_grouped_bar.html"
            grouped_bar_chart = PriceComparisonGroupedBarChart(formatted_data)
            grouped_bar_chart.generate_html(grouped_bar_output_file)

            print(
                f"File HTML Grouped Bar Chart đã được tạo thành công: {grouped_bar_output_file}"
            )

            # Tạo biểu đồ Step Line Chart 
            step_line_output_file = "DiscountFrequencyAnalysis/"+output_filenames[index] + "_step_line.html"
            step_line_chart = PriceEvolutionLineChart(formatted_data)
            step_line_chart.generate_highcharts_html(step_line_output_file)

            print(
                f"File HTML Step Line Chart đã được tạo thành công: {step_line_output_file}"
            )

            # Tạo biểu đồ Heatmap
            heatmap_output_file = "DiscountFrequencyAnalysis/"+output_filenames[index] + "_heatmap.html"
            heatmap_chart = DiscountFrequencyHeatmap(formatted_data)
            heatmap_chart.generate_html(heatmap_output_file)

            print(f"File HTML Heatmap đã được tạo thành công: {heatmap_output_file}")

            # Tạo biểu đồ Column Chart
            column_chart_output_file ="DiscountFrequencyAnalysis/"+ output_filenames[index] + "_column_chart.html"
            column_chart = TotalSavingsColumnChart(formatted_data)
            column_chart.generate_html(column_chart_output_file)

            print(
                f"File HTML Column Chart đã được tạo thành công: {column_chart_output_file}"
            )

            # Tạo biểu đồ Pie Chart  dưới dạng HTML
            pie_chart_output_file = "DiscountFrequencyAnalysis/"+output_filenames[index] + "_pie_chart.html"
            pie_chart = DiscountSavingsPieChart(formatted_data)
            pie_chart.generate_html(pie_chart_output_file)

            print(
                f"File HTML Pie Chart đã được tạo thành công: {pie_chart_output_file}"
            )

            return True

        except Exception as e:
            print(f"Lỗi khi xử lý game ID {game_id}: {str(e)}")
            return False


def visualize_PriceChart(id):
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Danh sách game IDs 
    game_ids = [
        id,
    ]

    # Danh sách các tên file HTML đầu ra tương ứng
    output_filenames = [
        "price_chart",
    ]

    # Gọi hàm để tạo các file HTML
    if generate_multiple_html_files(api_key, game_ids, shops_file, output_filenames):
        return True

    return False


visualize_PriceChart("018d937e-fcfb-7291-bf00-f651841d24d4")

