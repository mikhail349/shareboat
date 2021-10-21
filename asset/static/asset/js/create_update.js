function CreateUpdate() {
    const [errors, setErrors] = React.useState();
    const [action, setAction] = React.useState();
    const [files, setFiles] = React.useState([]);
    const [asset, setAsset] = React.useState();
    const [count, setCount] = React.useState(0);
    const [onFileUploadHover, setOnFileUploadHover] = React.useState(false);

    const [btnSaveOptions, setBtnSaveOptions] = React.useState({enabled: true, caption: "Сохранить"});
    const fileInputRef = React.createRef();
    const formRef = React.useRef();
    
    React.useEffect(() => {
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';
        const action = window.asset ? 1 : 0;
        
        setAsset(window.asset);    
        setAction(action);
        if (action == 1) {
            loadFiles(window.asset.id);
        }

        return () => {
            for (let file of files) {
                URL.revokeObjectURL(file.url);
            }
        }
    }, [])

    React.useEffect(() => {
        if (!formRef) return;

        const form = formRef.current;
        activateFormValidation(form);
        return () => deactivateFormValidation(form);
    }, [formRef]);

    function setBtnSaveEnabled(value) {
        const options = value ? {enabled: true, caption: "Сохранить"} : {enabled: false, caption: "Сохранение..."}
        setBtnSaveOptions(options);
    }

    async function loadFiles(id) {
        let newFiles = [...files];
        const response = await axios.get(`/file/api/get_assetfiles/${id}/`);
        for (let item of response.data.data) {
            let response = await fetch(item.url);
            let file = await response.blob();
            file.filename = item.filename;
            newFiles.push({
                blob: file,
                url: URL.createObjectURL(file)
            });
        }
        setFiles(newFiles);
    }

    async function AppendFiles(targetFiles) {
        const newFiles = [...files];

        for (let file of targetFiles) {
            newFiles.push({
                blob: file,
                url: URL.createObjectURL(file)
            });
        }
        setFiles(newFiles);            
    }

    function onFileInputChange(e) {
        const targetFiles = [...e.target.files];
        AppendFiles(targetFiles);
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
        setErrors();
        setBtnSaveEnabled(false);
        e.preventDefault();
        
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
            formData.append('file', file.blob, file.blob.filename);
        }

        try {
            const response = await axios.post(url, formData);
            window.location.href = response.data.redirect;
        } catch (e) {
            window.scrollTo(0, 0);
            setErrors(e.response.data.message);
            setBtnSaveEnabled(true);
        }
           
    }

    function onFileDelete(index) {     
        let newFiles = [...files];
        URL.revokeObjectURL(newFiles[index].url);
        newFiles.splice(index, 1);
        setFiles(newFiles);
    }

    function onDragEnter(e) {
        e.preventDefault();
        setCount((prevValue) => prevValue+1);
    }

    function onDragLeave(e) {
        e.preventDefault();
        setCount((prevValue) => prevValue-1);
    }

    function onDrop(e) {
        e.preventDefault();
        setCount(0);
        AppendFiles(e.dataTransfer.files);
    } 

    function isFileUploadHover() {
        return count > 0;
    }

    return (
        <React.Fragment>
            <form ref={formRef} onSubmit={onSave} className="needs-validation" noValidate>
                {
                    errors && <div className="alert alert-danger">{errors}</div>
                }
                <div className="mb-3">
                    <label for="name">Название актива</label>
                    <input type="text" id="name" name="name" className="form-control" placeholder="Введите название актива" autocomplete="false" aria-describedby="invalidInputName"
                        required 
                        value={asset && asset.name}
                        onChange={onNameChanged}
                    />
                    <div id="invalidInputName" class="invalid-feedback">
                        Введите название актива
                    </div>
                </div>
                <div className="mb-3">
                    <h4 className="mb-3">Фотографии</h4>
                    <div className={`file-upload-wrapper ${isFileUploadHover() ? "bg-light" : ""}`} 
                        onDragEnter={onDragEnter} 
                        onDragLeave={onDragLeave} 
                        onDrop={onDrop}
                        onDragOver={(e) => e.preventDefault()}
                    >    
                        <div className="row">
                            <input ref={fileInputRef} type="file" name="hidden_files" accept="image/*" multiple hidden onChange={onFileInputChange} />
                            {
                                files.map((file, index) => (
                                    <div key={index} className="col-md-3 mb-3">
                                        <div className="card box-shadow text-end">
                                            <img src={file.url} className="card-img" alt="Test" />  
                                            <div className="card-img-overlay">
                                                <div className="btn-group">
                                                    <button type="button" onClick={() => onFileDelete(index)} className="btn btn-sm btn-danger">
                                                        Удалить
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>                    
                                ))
                            }                
                        </div>
                        <div class="row align-items-center">
                            {
                                (
                                    <div class="col-auto">
                                        <button type="button" className="btn btn-primary" onClick={() => fileInputRef.current.click()}>Добавить {!!files.length && 'ещё '}фото</button>  
                                    </div> 
                                )
                            }

                            <div class="col-auto">
                                {
                                    isFileUploadHover() ? (
                                        <span className="text-success">
                                            Отпустите, чтобы добавить фото
                                        </span>  
                                    ) : !window.isMobile() && (
                                        <span className="text-muted">
                                            Или перетащите сюда фото
                                        </span>     
                                    )
                                }

                            </div>  
                        </div>
                    </div>
                    <hr/>
                    <button type="submit" className="btn btn-success" disabled={!btnSaveOptions.enabled}>{btnSaveOptions.caption}</button>
                </div>
            </form>
        </React.Fragment>
    )
}

ReactDOM.render(<CreateUpdate />, document.querySelector('#react_app'));