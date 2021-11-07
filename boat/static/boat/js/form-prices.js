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
            
        });
        setPrices(newPrices);
    }

    function deletePrice(index) {
        const newPrices = [...prices];
        newPrices.splice(index, 1);
        setPrices(newPrices);
    }

    function changeValue(e, index, fieldName) {
        console.log('onchange', fieldName)
        const newPrices = [...prices];
        newPrices[index][fieldName] = e.target.value;
        setPrices(newPrices); 
    }

    return(
        <>       
            {
                prices.map((price, index) => (        
                    <React.Fragment>
                        <div className="row align-items-center gy-3 mb-3">
                            <div className="col-auto">
                                <div className="form-floating">
                                    <select className="form-select" required value={price.type} onChange={(e) => changeValue(e, index, 'type')}>
                                        <option selected disabled value="">Выберите из списка</option>
                                        {
                                            priceTypes.map((priceType, index) => (
                                                <option value={priceType[0]}>{priceType[1]}</option>
                                            ))
                                        }
                                    </select>
                                    <label>Тип цены</label>
                                    <div className="invalid-tooltip">Выберите тип цены</div>
                                </div>
                            </div>
                            <div className="col-auto">
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
                            <div className="col-auto">
                                <div className="form-floating">                 
                                    <input type="date" className="form-control" placeholder="Укажите начало периода"
                                        required 
                                        value={price.start_date}
                                        onChange={(e) => changeValue(e, index, 'start_date')}
                                    />
                                    <label>Начало периода</label>
                                    <div className="invalid-tooltip">Укажите начало периода</div>
                                </div>
                            </div>
                            <div className="col-auto">
                                <div className="form-floating">                 
                                    <input type="date" className="form-control" placeholder="Укажите окончание периода"
                                        required 
                                        value={price.end_date}
                                        onChange={(e) => changeValue(e, index, 'end_date')}
                                    />
                                    <label>Окончание периода</label>
                                    <div className="invalid-tooltip">Укажите окончание периода</div>
                                </div>
                            </div>
                            <div className="col-md">
                                <button type="button" className="btn btn-outline-danger" onClick={() => deletePrice(index)}>
                                    Удалить
                                </button>                                          
                            </div>
                        </div>
                        <hr/>                     
                      </React.Fragment>             
                ))
            }
           
            <button type="button" className="btn btn-outline-primary" onClick={addPrice}>
                Добавить цену
            </button>  
        </>
    )
}
const appPrices = document.querySelector('#react_app_prices');
ReactDOM.render(<PricesList boatId={$(appPrices).attr("data-boat-id")} />, appPrices);