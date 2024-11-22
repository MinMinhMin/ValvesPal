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

function unixToDateString(unixTimestamp) {
    const date = new Date(unixTimestamp * 1000); // Multiply by 1000 to convert seconds to milliseconds
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}


function analyzing(){

    var list=update_history.update;
    document.getElementById("update").innerHTML+="All MAJOR updates: <br>";
    for(let i=0;i<list.length;i++){
        var date=unixToDateString(list[i][0]),title=list[i][1].replace(/^MAJOR\n/, '');
        document.getElementById("update").innerHTML+=`${date}: ${title} <br>`;
    }


}

async function initializeChart() {

    await loadDataset();
    analyzing();

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

