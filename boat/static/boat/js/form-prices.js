function PricesList(props) {

    const [prices, setPrices] = React.useState([]);
    const priceTypes = window.priceTypes;

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

    return(
        <>       
            {
                prices.map((price, index) => (        
                    <React.Fragment>
                        {
                            index != 0 && <hr/> 
                        }
                        <div className="row align-items-center g-3 mb-3">
                            <div className="col-lg-3">
                                <div className="form-floating">                 
                                    <input type="number" className="form-control" placeholder="Укажите цену" autocomplete="false"
                                        required 
                                        step=".01" min=".01" max="999999.99"  
                                        value={price.price}
                                        onChange={(e) => changeValue(e, index, 'price')}
                                    />
                                    <label>Цена</label>
                                    <div className="invalid-tooltip">Укажите цену</div>
                                </div>
                            </div>
                            <div className="col-6 col-lg-3">
                                <div className="form-floating">                 
                                    <input type="date" className="form-control" placeholder="Укажите начало действия"
                                        required 
                                        value={price.start_date}
                                        onChange={(e) => changeValue(e, index, 'start_date')}
                                    />
                                    <label>Начало действия</label>
                                    <div className="invalid-tooltip">Укажите начало действия</div>
                                </div>
                            </div>
                            <div className="col-6 col-lg-3">
                                <div className="form-floating">                 
                                    <input type="date" className="form-control" placeholder="Укажите окончание действия"
                                        required 
                                        value={price.end_date}
                                        onChange={(e) => changeValue(e, index, 'end_date')}
                                    />
                                    <label>Окончание действия</label>
                                    <div className="invalid-tooltip">Укажите окончание действия</div>
                                </div>
                            </div>
                            <div className="col-lg-auto">
                                <button type="button" className="btn btn-outline-danger form-control" onClick={() => deletePrice(index)}>
                                    Удалить
                                </button>                                     
                            </div>
                        </div>                    
                      </React.Fragment>             
                ))
            }
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