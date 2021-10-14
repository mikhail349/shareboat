function CreateUpdateReact() {
    const [files, setFiles] = React.useState([]);
    const fileInputRef = React.createRef();
    const [asset, setAsset] = React.useState();
    
    React.useEffect(() => {
        setAsset(window.asset);        
    }, [])

    function onFileInputChange(e) {
        setFiles([...files, ...e.target.files]);
    }

    console.log(asset);

    function onNameChanged(e) {
        setAsset((prevAsset) => {
            const newAsset = {...prevAsset}
            newAsset.name = e.target.value;
            return newAsset;
        })
    }

    function onSave(e) {
        e.preventDefault();
        console.log("submit");
    }

    return (
        <React.Fragment>
            <form onSubmit={onSave}>
                <div className="form-group">
                    <label for="name">Название актива</label>
                    <input type="text" id="name" name="name" className="form-control" placeholder="Введите название актива" 
                        required 
                        value={asset && asset.name}
                        onChange={onNameChanged}
                    />
                </div>
                <div className={`row ${!!files.length ? 'mb-3' : ''}`}>
                    <input ref={fileInputRef} type="file" name="files" multiple hidden onChange={onFileInputChange} />
                    {
                        files.map((file, index) => (
                            <div key={index} className="col-md-4">
                                <div className="card box-shadow text-center h-100">
                                    <img src={URL.createObjectURL(file)} class="card-img" />   
                                </div>
                            </div>                    
                        ))
                    }                
                </div>
                <button id="btnAddFiles" type="button" class="btn btn-primary" onClick={() => fileInputRef.current.click()}>Добавить {!!files.length && 'ещё '}фото</button>     
                <hr/>
                <button id="saveBtn" type="submit" class="btn btn-success">Сохранить</button>
            </form>
        </React.Fragment>
    )
}

ReactDOM.render(<CreateUpdateReact />, document.querySelector('#react_app'));