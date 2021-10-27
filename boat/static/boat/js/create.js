function Create() {
    const [btnSaveEnabled, setBtnSaveEnabled] = React.useState(true);

    async function onSave(data) {   
        
        const {boat, files} = data;    

        setBtnSaveEnabled(false);
        try {         
            const formData = new FormData();
            
            for (let key in boat) {
                formData.append(key, boat[key]);
            }
            
            for (let file of files) {
                formData.append('file', file.blob, file.blob.filename);
            }

            const response = await axios.post('/boats/api/create/', formData);
            window.location.href = response.data.redirect;
        } catch (e) {
            showErrorToast((e.response.data.message || e.response.data));
            setBtnSaveEnabled(true);
        }
    }

    return (
        <BoatForm 
            onSave={onSave}
            buttons={<button type="submit" className="btn btn-outline-success" disabled={!btnSaveEnabled}>Сохранить</button>}
        />
    )
}

ReactDOM.render(<Create />, document.querySelector('#react_app'));