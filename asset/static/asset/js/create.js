function Create() {
    const [errors, setErrors] = React.useState();
    const [files, setFiles] = React.useState([]);
    const [asset, setAsset] = React.useState();

    const [btnSaveOptions, setBtnSaveOptions] = React.useState({enabled: true, caption: "Сохранить"});
    const formRef = React.useRef();
    useAxios();

    React.useEffect(() => {     
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
                    <button type="submit" className="btn btn-outline-success" disabled={!btnSaveOptions.enabled}>{btnSaveOptions.caption}</button>
                </div>
            </form>
        </React.Fragment>
    )
}

ReactDOM.render(<Create />, document.querySelector('#react_app'));