const nbr = 20, startYear_month = "2021-11", endYear_month = "2024-11",
      btn = document.getElementById('play-pause-button'),
      input = document.getElementById('play-range');

let map=new Map();
let top5=new Map();
let dataset, chart,data,category,image;
let peak ="None";
let biggestStep_value=0,biggestStep_Title="None",biggestStep_content="";
let biggestDrop_value=0,biggestDrop_Title="None",biggestDrop_content="";
let onTop5forLongest_Title="None",onTop5forLongest_Value=0;
let highgestPlayerNumbers_Title="None",highestPlayerNumbers_Value=0,highestPlayerNumbers_time="";
function getDateRange(A, B) {
    const startDate = new Date(A + "-01");
    const endDate = new Date(B + "-01");
    const dates = [];

    while (startDate <= endDate) {
        const year = startDate.getFullYear();
        const month = String(startDate.getMonth() + 1).padStart(2, '0');
        dates.push(`${year}-${month}`);
        startDate.setMonth(startDate.getMonth() + 1);
    }

    return dates;
}

const time = getDateRange(startYear_month, endYear_month);

async function loadDataset() {
    data = await fetch('dataset.json').then(response => response.json());
    dataset=data.Data;
    category=data.Category;
    image=data.Image;
}


function analyzing(){
    sarr=getData(time[input.value]);
    for(let i=0;i<20;i++){
        if (sarr[i][1]>highestPlayerNumbers_Value){
            highestPlayerNumbers_Value=sarr[i][1];
            highgestPlayerNumbers_Title=sarr[i][0];
            highestPlayerNumbers_time=time[input.value];

        }
        if (!map.has(sarr[i][0])){
            map.set(sarr[i][0],[]);
        }
        map.get(sarr[i][0]).push(i);
        if (i<5){
            if(!top5.has(sarr[i][0])){
                top5.set(sarr[i][0],0);
            }
            top5.set(sarr[i][0], top5.get(sarr[i][0]) + 1);
        }
    }
    map.forEach((value, key) => {
        for (let i=1;i<value.length;i++){
            if(value[i-1]-value[i]>biggestStep_value){
                biggestStep_value=value[i-1]-value[i];
                biggestStep_Title=key;
                biggestStep_content=`( No.${value[i-1]+1} -> No.${value[i]+1} at ${time[input.value]})`
            }
            if(value[i]-value[i-1]>biggestDrop_value){
                biggestDrop_value=value[i]-value[i-1];
                biggestDrop_Title=key;
                biggestDrop_content=`( No.${value[i-1]+1} -> No.${value[i]+1} at ${time[input.value]})`
            }
        }

    });
    top5= new Map([...top5.entries()].sort((a, b) => b[1]-a[1]));
    onTop5forLongest_Title=top5.keys().next().value;
    onTop5forLongest_Value=top5.get(onTop5forLongest_Title);
    document.getElementById("longestTop5").textContent=`${onTop5forLongest_Title} nằm trong Top 5 lâu nhất với ${onTop5forLongest_Value} tháng`;
    document.getElementById("highgestPlayers").textContent = `Số lượng người chơi cao nhất là ${highestPlayerNumbers_Value} (${highgestPlayerNumbers_Title}) vào tháng ${highestPlayerNumbers_time}`;
    document.getElementById("biggestStep").textContent = `Bước nhảy lớn nhất: ${biggestStep_Title} ${biggestStep_content}`;
    document.getElementById("biggestDrop").textContent = `Sụt giảm lớn nhất: ${biggestDrop_Title} ${biggestDrop_content}`;
}


function getData(year_month) {
    var sarr = Object.entries(dataset)
    .map(([gameName, gameData]) => [gameName, Number(gameData[year_month])])
    .sort((a, b) => b[1] - a[1])
    .slice(0, nbr);
    peak=sarr[0][0];
    return sarr // Return top `nbr` games
}

function getSubtitle() {
    const population = (getData(time[input.value])[0][1] / 1000000000).toFixed(2);

    return `<span style="font-size: 50px">${time[input.value]}
            <img src="${image[peak]}" alt="" style="width: 60px; vertical-align: middle;"
        </span><br>
<span style="font-size: 22px">Top: <b>${peak}</b> </span>`;
}

async function initializeChart() {
    await loadDataset();
    document.getElementById("description").innerHTML = `Biểu đồ thanh hiển thị xếp hạng hàng tháng của các trò chơi thuộc thể loại ${category} từ tháng 11 năm 2021 đến tháng 11 năm 2024`;
    chart = Highcharts.chart('container', {
        chart: {
            animation: { duration: 1000 },
            marginRight: 50,
            style: {
                fontFamily: 'MyCustomFont',
                fontSize: '13px'
            }
        },

        title: { text: 'Xếp hạng', align: 'left' },
        subtitle: {
            useHTML: true,
            text: getSubtitle(),
            floating: true,
            align: 'right',
            verticalAlign: 'middle',
            y: -80,
            x: -100
        },
        legend: { enabled: false },
        xAxis: { type: 'category' },
        yAxis: {
            opposite: true,
            tickPixelInterval: 150,
            title: { text: null }
        },
        plotOptions: {
            series: {
                animation: false,
                groupPadding: 0,
                pointPadding: 0.1,
                borderWidth: 0,
                colorByPoint: true,
                dataSorting: {
                    enabled: true,
                    matchByName: true
                },
                type: 'bar',
                dataLabels: { enabled: true }
            }
        },
        series: [
            {
                type: 'bar',
                name: startYear_month,
                data: getData(startYear_month)
            }
        ],
        responsive: {
            rules: [{
                condition: { maxWidth: 550 },
                chartOptions: {
                    xAxis: { visible: false },
                    subtitle: { x: 0 },
                    plotOptions: {
                        series: {
                            dataLabels: [{ enabled: true, y: 8 }]
                        }
                    }
                }
            }]
        }
    });
}

async function update(increment = 0) {
    if (increment) input.value = parseInt(input.value) + increment;

    if (time[input.value] === endYear_month) {
        pause(btn);

    }

    analyzing();

    chart.update({
        subtitle: { text: getSubtitle() }
    }, false, false, false);

    chart.series[0].update({
        name: time[input.value],
        data: getData(time[input.value])
    });
}

function pause(button) {
    button.title = 'play';
    button.className = 'fa fa-play';
    clearInterval(chart.sequenceTimer);
    chart.sequenceTimer = undefined;
}

function play(button) {
    button.title = 'pause';
    button.className = 'fa fa-pause';
    chart.sequenceTimer = setInterval(() => update(1), 1500);
}

btn.addEventListener('click', () => chart.sequenceTimer ? pause(btn) : play(btn));

input.addEventListener('click', () => update());

// Initialize the chart
initializeChart();
