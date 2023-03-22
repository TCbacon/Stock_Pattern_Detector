
function setUserInputs(data){
    const stockDateRangeText = document.getElementById("date-range-text-id")
    const rsiPeriodText = document.getElementById("rsi-period-text-id")
    const intervalText = document.getElementById("interval-text-id")

    stockDateRangeText.innerText = `Date Range: ${data["start_date"]} - ${data["end_date"]}`
    rsiPeriodText.innerText = `RSI: ${data["rsi_period"]}`
    intervalText.innerText = `Interval: ${data["interval"]} seconds`
}

async function retrieve_latest_data(){
    const requestOptions = {
        method: 'GET'
      };

    try{

        const loadingStockMsg = document.getElementById("loading-stock-id")

        let response = await fetch("/get_latest_data", requestOptions)
        let data = await response.json()

        if(Object.keys(data).length === 0){
            loadingStockMsg.innerText = "";
            return
        }

        const stockDataList = document.getElementById("stocks-list-id")
        stockDataList.innerHTML = "";
        loadingStockMsg.innerText = "";

        for(let key in data){
            if (data.hasOwnProperty(key)) {
                const li = document.createElement('li')
                
                let trend = data[key][1]
                switch(trend){
                    case 'bullish':
                        li.className = 'bullish stock'
                        break
                    case 'bearish':
                        li.className = 'bearish stock'
                        break
                    default:
                        li.className = 'flat stock'
                        break
                }

                li.textContent = `${key}, ${data[key][0]}, ${data[key][1]}, ${data[key][2]}, ${data[key][3]}`
                stockDataList.appendChild(li)
            }
        }
    }

    catch(err){
        console.log(err);
    }
}


async function runIntervalDetection(){
    const requestOptions = {
        method: 'GET'
    };

    try{
        let response = await fetch("/run_interval_detection", requestOptions)
        let data = await response.json()
        document.getElementById("status-msg-id").textContent = data.message
    }
    catch(err){
        console.log(err)
    }
}


async function sendInputInterval(){

    const form1 = document.getElementById("form1-id")
    const formData = new FormData(form1)

    const interval = formData.get('interval')
    const rsi = formData.get('rsi_period')
    const stock_period = formData.get('stock_period')


    const requestOptions = {
        method: 'POST',
        headers:{ "Content-Type": "application/json" },
        body: JSON.stringify({ interval: interval, rsi_period: rsi, stock_period: stock_period})
    };

    try{
        let response = await fetch("/user_input", requestOptions)
        let data = await response.json()

        const submitMsg = document.getElementById("submit-msg-id")
        submitMsg.textContent = data.message
        setUserInputs(data)


        setTimeout(() => {
            submitMsg.textContent = '';
        }, 3000);

    }
    catch(err){
        console.log(err)
    }
}


async function getDefaultSettings(){
    const requestOptions = {
        method: 'GET'
    };

    try{
        let response = await fetch("/get_default_settings", requestOptions)
        let data = await response.json()
        setUserInputs(data)
    }
    catch(err){
        console.log(err)
    }
}

runIntervalDetection()
getDefaultSettings()
setInterval(retrieve_latest_data, 10000)