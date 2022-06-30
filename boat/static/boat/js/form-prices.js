function PricesList(props) {

    const [prices, setPrices] = React.useState([]);
    const now = new Date(new Date().toDateString());

    React.useEffect(() => {
        const newPrices = [];
        for (const price of window.prices) {
            newPrices.push({
                ...price.fields,
                pk: price.pk
            })
        }
        setPrices(newPrices);
    }, [])

    React.useEffect(() => {
        window.prices = prices;
    }, [prices])

    function addPrice() {
        const newPrices = [...prices];
        newPrices.push({
            type: 0
        });
        setPrices(newPrices);
    }

    function deletePrice(index) {
        const newPrices = [...prices];
        newPrices.splice(index, 1);
        setPrices(newPrices);
    }

    function changeValue(e, index, fieldName) {
        const newPrices = [...prices];
        newPrices[index][fieldName] = e.target.value;
        setPrices(newPrices); 
    }

    function getPriceStateCss(price) {

        if (price.end_date) {
            let endDate = new Date(new Date(price.end_date).toDateString());
            if (endDate < now) {
                return <div className="badge bg-danger ms-3 align-self-center fw-normal">Устаревшая</div>
            }     
        }

        if (price.start_date) {
            let startDate = new Date(new Date(price.start_date).toDateString());
            if (startDate > now) {
                return <div className="badge bg-light text-dark ms-3 align-self-center fw-normal">На будущее</div>
            }     
        }

        if (price.start_date && price.end_date) {
            let startDate = new Date(new Date(price.start_date).toDateString());
            let endDate = new Date(new Date(price.end_date).toDateString());
            if (startDate <= now <= endDate) {
                return <div className="badge bg-success ms-3 align-self-center fw-normal">Актуальная</div>
            }
        }    

    }

    return(
        <>       
            <div className="row g-3 mb-3">
            {
                prices.map((price, index) => (
                    <div key={index} className="col-lg-4">
                        <div className="card">
                            <div className="card-body">
                                <div className="d-flex mb-2">
                                    <h5 className="card-title mb-0">Цена #{index+1}</h5>
                                    {getPriceStateCss(price)}
                                    <button type="button" className="btn-close ms-auto" onClick={() => deletePrice(index)}></button>
                                </div>
                                <div className="form-floating mb-2">                 
                                    <input type="number" className="form-control" placeholder="Укажите цену" autocomplete="false"
                                        required 
                                        step=".01" min=".01" max="999999.99"  
                                        value={price.price}
                                        onChange={(e) => changeValue(e, index, 'price')}
                                    />
                                    <label>Цена</label>
                                    <div className="invalid-tooltip">Укажите цену</div>
                                </div>
                                <div className="form-floating mb-2">                 
                                    <input type="date" className="form-control" placeholder="Укажите начало действия"
                                        required 
                                        value={price.start_date}
                                        onChange={(e) => changeValue(e, index, 'start_date')}
                                    />
                                    <label>Начало действия</label>
                                    <div className="invalid-tooltip">Укажите начало действия</div>
                                </div>
                                <div className="form-floating mb-2">                 
                                    <input type="date" className="form-control" placeholder="Укажите окончание действия"
                                        required 
                                        value={price.end_date}
                                        onChange={(e) => changeValue(e, index, 'end_date')}
                                    />
                                    <label>Окончание действия</label>
                                    <div className="invalid-tooltip">Укажите окончание действия</div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))
            }
            </div>
            <div className="row row-cols-lg-auto align-items-center gy-3 mb-3">
                <div className="col-md">
                    <button type="button" className="btn btn-outline-primary form-control" onClick={addPrice}>
                        Добавить цену
                    </button>  
                </div>  
            </div>  
        </>
    )
}
const appPrices = document.querySelector('#react_app_prices');
ReactDOM.render(<PricesList boatId={$(appPrices).attr("data-boat-id")} />, appPrices);