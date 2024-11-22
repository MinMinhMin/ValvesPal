let dataset,title,counts,update_history,predicts;
let plotLines;

async function loadDataset() {
    dataset = await fetch('playersCount.json').then(response => response.json());
    title=dataset.title;
    counts=dataset.counts;
    predicts=dataset.predicts;
    predicts.unshift(counts[0])
    update_history=await fetch('UpdateHistory.json').then(response => response.json());
    plotLines = update_history.update.map(item => ({
        color: '#FF0000', // Red
        width: 2,
        value: parseInt(item[0]) * 1000, // Convert Unix timestamp to milliseconds
        dashStyle: 'Dot'
    }));
}

async function initializeChart() {

    await loadDataset();

    document.getElementById("title").textContent="Player count of "+title;


    Highcharts.stockChart('container', {

        chart:{
            zooming:{
                mouseWheel:{
                    enabled:false,
                }
            },

            style:{
                fontFamily: 'MyCustomFont',
                fontSize: '13px'
            }
        },

        navigator: {
            enabled: false
        },
        scrollbar: {
            barBorderRadius: 0,
            barBorderWidth: 1,
            buttonsEnabled: true,
            height: 14,
            margin: 0,
            rifleColor: '#333',
            trackBackgroundColor: '#f2f2f2',
            trackBorderRadius: 0,
            enabled: false,
        },

        rangeSelector: {
            selected: 5,
            enabled: false
        },

        series: [{
            name: 'Players: ',
            data: counts
        },{
            name:"Prediction: ",
            data: predicts,
            dashStyle:'Dash'
        }],
        xAxis: {
            plotLines: plotLines,
        },

    });


}



initializeChart();