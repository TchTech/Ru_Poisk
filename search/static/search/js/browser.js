// var OptionsModal = document.getElementById('advanced_options_modal')
// var OptionsInput = document.getElementById('advanced_options_btn')
    
// OptionsModal.addEventListener('shown.bs.modal', function () {
//     OptionsInput.focus()
// })

document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });

var SiteInput = document.getElementById("site_input")
var QueryInput = document.getElementById("query_input")

if(sessionStorage.site != undefined){
    SiteInput.value = sessionStorage.site
}

if(sessionStorage.query != undefined){
    QueryInput.value = sessionStorage.query
}

var OptionsSubmitBtn = document.getElementById('advanced_options_submit_btn')
var FormSubmitButton = document.getElementById("form-submit")

OptionsSubmitBtn.onclick= function() {
    let Depth = Math.abs(document.getElementById('depth').value)
    if(Depth == "" || Depth == 0 || Depth == undefined){
        Depth = 30
    }
    let RankMethod = document.getElementById('rank-method').value
    let SitemapMethod = document.getElementById('sitemap-method').value
    document.cookie = "depth="+Depth+";"
    document.cookie = "rank_method="+RankMethod+";"
    document.cookie = "sitemap_method="+SitemapMethod+";"
    alert("Данные успешно сохранены!")
    console.log("depth="+Depth+"; rank_method="+RankMethod+"; sitemap_method="+SitemapMethod+";")
};

FormSubmitButton.onclick = function(){
    sessionStorage.site = SiteInput.value;
    sessionStorage.query = QueryInput.value;
}