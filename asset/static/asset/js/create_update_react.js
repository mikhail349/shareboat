function CreateUpdateReact() {
    const [action, setAction] = React.useState();
    const [files, setFiles] = React.useState([]);
    const [asset, setAsset] = React.useState();
    const [btnSaveEnabled, setBtnSaveEnabled] = React.useState(true);
    const fileInputRef = React.createRef();
    
    React.useEffect(() => {
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';
        const action = window.asset ? 1 : 0;
        
        setAsset(window.asset);    
        setAction(action);
        if (action == 1) {
            loadFiles(window.asset.id);
        }
    }, [])

    async function loadFiles(id) {
        let res = [];
        const response = await axios.get(`/file/api/get_assetfiles/${id}/`);
        for (let item of response.data.data) {
            let response = await fetch(item.url);
            let file = await response.blob();
            file.filename = item.filename;
            res.push(file);
        }
        setFiles([...files, ...res]);
    }

    function onFileInputChange(e) {
        setFiles([...files, ...e.target.files]);
        fileInputRef.current.value = null;
    }

    function onNameChanged(e) {
        setAsset((prevAsset) => {
            const newAsset = {...prevAsset}
            newAsset.name = e.target.value;
            return newAsset;
        })
    }

    function onSave(e) {
        e.preventDefault();
        setBtnSaveEnabled(false);
        
        if (action == 0) {
            post('/asset/api/create/');
        } else {
            post(`/asset/api/update/${asset.id}/`);
        }
        
    }

    async function post(url) {
        const formData = new FormData();
        formData.append('name', asset.name);

        for (let file of files) {
            formData.append('file', file, file.filename);
        }

        const response = await axios.post(url, formData);
        window.location.href = response.data.redirect;
    }

    return (
        <React.Fragment>
            <form onSubmit={onSave} autocomplete="off">
                <div className="form-group">
                    <label for="name">Название актива</label>
                    <input type="text" id="name" name="name" className="form-control" placeholder="Введите название актива" 
                        required 
                        value={asset && asset.name}
                        onChange={onNameChanged}
                    />
                </div>
                <div class="form-group">
                    <h4 class="mb-3">Фотографии</h4>
                    <div className={`row ${!!files.length ? 'mb-3' : ''}`}>
                        <input ref={fileInputRef} type="file" name="files" multiple hidden onChange={onFileInputChange} />
                        {
                            files.map((file, index) => (
                                <div key={index} className="col-md-4">
                                    <div className="card box-shadow text-center h-100">
                                        <img src={URL.createObjectURL(file)} class="card-img" />  
                                        <div class="card-img-overlay">
                                            <div class="card-footer d-flex justify-content-between align-items-center">
                                                <div class="btn-group">
                                                    <a href="update/{{ asset.id }}" data-id="{{ asset.id }}" class="btn btn-sm btn-outline-primary">Открыть</a>
                                                </div>
                                            </div> 
                                        </div>
                                    </div>
                                </div>                    
                            ))
                        }                
                    </div>
                    <button type="button" class="btn btn-primary" onClick={() => fileInputRef.current.click()}>Добавить {!!files.length && 'ещё '}фото</button>     
                    <hr/>
                    <button type="submit" class="btn btn-success" disabled={!btnSaveEnabled}>Сохранить</button>
                </div>
            </form>
        </React.Fragment>
    )
}

ReactDOM.render(<CreateUpdateReact />, document.querySelector('#react_app'));