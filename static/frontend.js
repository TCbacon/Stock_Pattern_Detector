
function setUserInputs(data){
    const stockDateRangeText = document.getElementById("date-range-text-id")
    const rsiPeriodText = document.getElementById("rsi-period-text-id")
    const intervalText = document.getElementById("interval-text-id")
    const fileNameText = document.getElementById("file-name-text-id")

    stockDateRangeText.innerText = `Date Range: ${data["start_date"]} - ${data["end_date"]}`
    rsiPeriodText.innerText = `RSI: ${data["rsi_period"]}`
    intervalText.innerText = `Interval: ${data["interval"]} seconds`
    fileNameText.innerText = `File: ${data["file_name"]}`
}

async function retrieve_latest_data(){
    const requestOptions = {
        method: 'GET'
      };

    try{

        
        const stockDataList = document.getElementById("stocks-list-id")
        const loadingStockMsg = document.getElementById("loading-stock-id")

        let response = await fetch("/get_latest_data", requestOptions)
        let data = await response.json()

        if(Object.keys(data).length === 0){
            stockDataList.innerHTML = "";
            loadingStockMsg.innerText = "No data to display. Choose a csv file containing stock symbol and name";
            return
        }

        stockDataList.innerHTML = "";
        loadingStockMsg.innerText = "";

        for(let key in data){
            if (data.hasOwnProperty(key) && data[key].length == 5) {
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

                li.textContent = `${data[key][0]}, $${data[key][1]}, ${data[key][2]}, ${data[key][3]}, ${data[key][4]}`
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

    const requestOptions = {
        method: 'POST',
        body: formData
    };

    try{
        let response = await fetch("/user_input", requestOptions)
        let data = await response.json()

        const submitMsg = document.getElementById("submit-msg-id")
        submitMsg.textContent = data.message

        if(data.status === 200){
            setUserInputs(data)
        }

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