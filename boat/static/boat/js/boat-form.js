$(document).ready(() => {

    class InputValidator {
        constructor(input, tooltip) {
            this.input = input;
            this.tooltip = $(input).siblings(".invalid-tooltip");
            this.errorsList = [];
        }

        addError(msg, f) {
            if (f(this.input.val())) {
                this.errorsList.push(msg);
            }
        }

        validate() {
            const error = this.errorsList.join("\n");
            this.input[0].setCustomValidity(error);
            this.tooltip.text(error);            
        }
    }

    $("input[name=name]").on("input", (e) => {
        const length = new InputValidator($("input[name=name]"));
        length.addError("Введите название лодки", (val) => !val);
        length.addError("Слишком длинное название", (val) => val.length > 255);
        length.validate();
    })

    $("input[name=length]").on("input", (e) => {
        const length = new InputValidator($("input[name=length]"));
        length.addError("Укажите длину лодки", (val) => !val || val < 0.1);
        length.addError("Слишком длинная лодка", (val) => val > 999.9);
        length.validate();
    })

    $("input[name=width]").on("input", () => {
        const length = new InputValidator($("input[name=width]"));
        length.addError("Укажите ширину лодки", (val) => !val || val < 0.1);
        length.addError("Слишком широкая лодка", (val) => val > 99.9);
        length.validate();
    })

    $("input[name=draft]").on("input", () => {
        const length = new InputValidator($("input[name=draft]"));
        length.addError("Укажите осадку лодки", (val) => !val || val < 0.1);
        length.addError("Слишком большая осадка", (val) => val > 9.9);
        length.validate();
    })

})

function BoatForm(props) {
    
    const [files, setFiles] = React.useState([]);
    const [boat, setBoat] = React.useState();
    const formRef = React.useRef();
    useAxios();

    React.useEffect(() => {     
        if (props.boat) {
            setBoat(props.boat);
        }
        return () => {
            for (let file of files) {
                URL.revokeObjectURL(file.url);
            }
        }
    }, []);

    React.useEffect(() => {
        if (props.files) {
            setFiles(props.files);
        }
    }, [props.files])

    function onNameChanged(e) {
        setBoat((prevBoat) => {
            const newBoat = {...prevBoat}
            newBoat.name = e.target.value;
            return newBoat;
        })
    }

    function onValueChanged(e) {
        const fieldName = e.target.getAttribute('name');
        setBoat((prevBoat) => {
            const newBoat = {...prevBoat}
            newBoat[fieldName] = e.target.value;
            return newBoat;
        })
    }

    function onSave(e) {
        e.preventDefault();                
        props.onSave({boat: boat, files: files});
    }

    async function appendFiles(targetFiles) {
        const newFiles = [...files];
        for (let file of targetFiles) {
            newFiles.push({
                blob: file,
                url: URL.createObjectURL(file)
            });
        }
        setFiles(newFiles);            
    }

    function deleteFile(index) {     
        let newFiles = [...files];
        URL.revokeObjectURL(newFiles[index].url);
        newFiles.splice(index, 1);
        setFiles(newFiles);
    }

    return (
        <>
            <form ref={formRef} onSubmit={onSave} className="needs-validation" noValidate>
                {
                    props.errors && <div className="alert alert-danger">{props.errors}</div>
                }
                <h4 className="mb-3">Основная информация</h4>
                <div className="form-floating mb-3">                 
                    <input type="text" id="name" name="name" className="form-control" placeholder="Введите название лодки" autocomplete="false" aria-describedby="invalidInputName"             
                        required
                        value={boat && boat.name}
                        onChange={onNameChanged}
                    />
                    <label for="name">Название лодки</label>
                    <div class="invalid-tooltip">Введите название лодки</div>
                </div>
                <div className="row">
                    <div className="col-auto">
                        <div className="form-floating mb-3">                 
                            <input type="number" name="length" className="form-control" placeholder="Укажите длину лодки" autocomplete="false"
                                step=".1"
                                required
                                value={boat && boat.length}
                                onChange={onValueChanged}
                            />
                            <label for="length">Длина, м.</label>
                            <div class="invalid-tooltip">Укажите длину лодки</div>
                        </div>
                    </div>
                    <div className="col-auto">
                        <div className="form-floating mb-3">                 
                            <input type="number" name="width" className="form-control" placeholder="Укажите ширину лодки" autocomplete="false"
                                step=".1"
                                required         
                                value={boat && boat.width}
                                onChange={onValueChanged}
                            />
                            <label for="length">Ширина, м.</label>
                            <div class="invalid-tooltip">Укажите ширину лодки</div>
                        </div>
                    </div>
                    <div className="col-auto">
                        <div className="form-floating mb-3">                 
                            <input type="number" name="draft" className="form-control" placeholder="Укажите осадку лодки" autocomplete="false"
                                step=".1"
                                required 
                                value={boat && boat.draft}
                                onChange={onValueChanged}
                            />
                            <label for="length">Осадка, м.</label>
                            <div class="invalid-tooltip">Укажите осадку лодки</div>
                        </div>
                    </div>
                </div>
                <div className="mb-3">
                    <h4 className="mb-3">Фотографии</h4>
                    <FilesList 
                        files={files} 
                        onFilesAdd={appendFiles} 
                        onFileDelete={deleteFile} 
                    />
                </div>
                <hr/>
                {
                    props.buttons
                }
            </form>

            <div className="toast-container position-absolute p-3 top-0-header start-50 translate-middle-x">
                <div id="toast" className="toast align-items-center text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div className="d-flex">
                        <div className="toast-body"></div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            </div>
        </>
    )
}

function FilesList(props) {
    const [count, setCount] = React.useState(0);
    const fileInputRef = React.createRef();

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
        props.onFilesAdd(e.dataTransfer.files);
    }

    function isFileUploadHover() {
        return count > 0;
    }

    function onFileInputChange(e) {
        props.onFilesAdd(e.target.files);
        fileInputRef.current.value = null; 
    }

    return (
        <div className={`file-upload-wrapper ${isFileUploadHover() ? "bg-light" : ""}`} 
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
        >    
            <div className="row">
                <input ref={fileInputRef} type="file" name="hidden_files" accept="image/*" multiple hidden onChange={onFileInputChange} />
                {
                    props.files.map((file, index) => (
                        <div key={index} className="col-md-3 mb-3">
                            <div className="card box-shadow text-end">
                                <img src={file.url} className="card-img" />  
                                <div className="card-img-overlay">
                                    <div className="btn-group">
                                        <button type="button" className="btn btn-sm btn-danger" onClick={() => props.onFileDelete(index)}>
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
                <div class="col-auto">
                    <button type="button" className="btn btn-outline-primary" onClick={() => fileInputRef.current.click()}>
                        Добавить {!!props.files.length && 'ещё '}фото
                    </button>  
                </div> 
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
    )
}