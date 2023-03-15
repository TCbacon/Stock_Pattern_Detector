async function generate_stock_csv() {

    const requestOptions = {
        method: 'GET'
      };

    try{

        const csv_msg = document.getElementById("csv-msg-id")

        csv_msg.textContent = "Generating..."
        let response = await fetch("/generate_csv", requestOptions)
        let data = await response.json()
        let msg = data.message

        csv_msg.textContent = msg
        setTimeout(() => {
            csv_msg.textContent = '';
        }, 3000);

    }

    catch(err){
        console.log(err);
    }
}
