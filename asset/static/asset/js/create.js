function Create() {
    const [errors, setErrors] = React.useState();
    const [files, setFiles] = React.useState([]);
    const [count, setCount] = React.useState(0);

    const [btnSaveOptions, setBtnSaveOptions] = React.useState({enabled: true, caption: "Сохранить"});
    const fileInputRef = React.createRef();
    const formRef = React.useRef();
    
    React.useEffect(() => {
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';
        
        return () => {
            for (let file of files) {
                URL.revokeObjectURL(file.url);
            }
        }
    }, [])

    function setBtnSaveEnabled(value) {
        const options = value ? {enabled: true, caption: "Сохранить"} : {enabled: false, caption: "Сохранение..."}
        setBtnSaveOptions(options);
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
        e.preventDefault();
        
        setErrors();
        setBtnSaveEnabled(false);
        try {
            
            const formData = new FormData(formRef.current);
            //formData.append('name', asset.name);

            for (let file of files) {
                formData.append('file', file.blob, file.blob.filename);
            }

            const response = await axios.post('/asset/api/create/', formData);
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
                <h4 className="mb-3">Основная информация</h4>
                <div className="form-floating mb-3">                 
                    <input type="text" id="name" name="name" className="form-control" placeholder="Введите название актива" autocomplete="false" aria-describedby="invalidInputName"
                        required 
                        value={asset && asset.name}
                        onChange={onNameChanged}
                    />
                    <label for="name">Название актива</label>
                    <div class="invalid-tooltip">Введите название актива</div>
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
                                            <img src={file.url} className="card-img" />  
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
                                        <button type="button" className="btn btn-outline-primary" onClick={() => fileInputRef.current.click()}>Добавить {!!files.length && 'ещё '}фото</button>  
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
                                            Или перетащите фото сюда
                                        </span>     
                                    )
                                }

                            </div>  
                        </div>
                    </div>
                    <hr/>
                    <button type="submit" className="btn btn-outline-success" disabled={!btnSaveOptions.enabled}>{btnSaveOptions.caption}</button>
                </div>
            </form>
        </React.Fragment>
    )
}

ReactDOM.render(<Create />, document.querySelector('#react_app'));