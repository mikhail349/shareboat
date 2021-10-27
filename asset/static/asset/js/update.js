function Update() {
    const [errors, setErrors] = React.useState();
    const [files, setFiles] = React.useState([]);
    const [asset, setAsset] = React.useState();

    const [btnSaveOptions, setBtnSaveOptions] = React.useState({enabled: true, caption: "Сохранить"});
    const formRef = React.useRef();
    useAxios();
    
    React.useEffect(() => {        
        setAsset(window.asset);    
        loadFiles(window.asset.id);

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

    async function loadFiles(id) {
        setBtnSaveOptions({enabled: false, caption: "Загрузка..."});
        try {
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
        } finally {
            setBtnSaveEnabled(true);
        }
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

    function onNameChanged(e) {
        setAsset((prevAsset) => {
            const newAsset = {...prevAsset}
            newAsset.name = e.target.value;
            return newAsset;
        })
    }

    async function onSave(e) {
        e.preventDefault();
        
        setErrors();
        setBtnSaveEnabled(false);
        try {         
            const formData = new FormData(formRef.current);

            for (let file of files) {
                formData.append('file', file.blob, file.blob.filename);
            }

            const response = await axios.post(`/asset/api/update/${asset.id}/`, formData);
            window.location.href = response.data.redirect;
        } catch (e) {
            window.scrollTo(0, 0);
            setErrors((e.response.data.message || e.response.data));
            setBtnSaveEnabled(true);
        }
    }

    async function onDelete(e) {
        e.preventDefault();
        $('#confirmDeleteModal').modal('hide');
        try {
            await axios.post(`/asset/api/delete/${asset.id}/`);
            window.location.href = '/asset/';
        } catch(e) {
            showErrorToast((e.response.data.message || e.response.data));
        }
    }

    function onFileDelete(index) {     
        let newFiles = [...files];
        URL.revokeObjectURL(newFiles[index].url);
        newFiles.splice(index, 1);
        setFiles(newFiles);
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
                    <FilesList 
                        files={files} 
                        onFilesAdd={AppendFiles} 
                        onFileDelete={onFileDelete} 
                    />
                    <hr/>
                    <div className="row g-3">
                        <div className="col-auto">
                            <button type="submit" className="btn btn-outline-success" disabled={!btnSaveOptions.enabled}>{btnSaveOptions.caption}</button>                          
                        </div>
                        <div className="col-auto">
                            <button type="button" className="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal">Удалить</button>
                        </div>
                    </div>
                </div>
            </form>

            <div id="confirmDeleteModal" className="modal" tabindex="-1" role="dialog" aria-labelledby="confirmDeletionModalLabel" style={{display: 'none'}}>
                <div className="modal-dialog modal-dialog-centered" role="document">
                    <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title" id="confirmDeletionModalLabel">Удаление актива</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div className="modal-body">
                        <p>Удалить актив?</p>
                    </div>
                    <div className="modal-footer">
                        <button id="btnConfirmDelete" type="button" className="btn btn-danger" onClick={onDelete}>Удалить</button>
                        <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>               
                    </div>
                    </div>
                </div>
            </div>

            <div className="toast-container position-absolute p-3 top-0-header start-50 translate-middle-x">
                <div id="toast" className="toast align-items-center text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div className="d-flex">
                        <div className="toast-body"></div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            </div>
        </React.Fragment>
    )
}

ReactDOM.render(<Update />, document.querySelector('#react_app'));