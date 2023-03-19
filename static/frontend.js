async function retrieve_latest_data(){
    const requestOptions = {
        method: 'GET'
      };

    try{
        let response = await fetch("/get_latest_data", requestOptions)
        let data = await response.json()

        if(Object.keys(data).length === 0){
            return
        }

        const stockDataList = document.getElementById("stocks-list-id")
        stockDataList.innerHTML = "";

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


async function startIntervalData(){
    const requestOptions = {
        method: 'GET'
    };

    try{
        let response = await fetch("/run_interval_detection", requestOptions)
        let data = await response.json()
        console.log(data.message)
        document.getElementById("market-closed-id").textContent = data.message
    }
    catch(err){
        console.log(err)
    }
}

startIntervalData()
setInterval(retrieve_latest_data, 10000)