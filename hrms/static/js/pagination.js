(function(window){

    function lignePaginate(){
        var _lignePaginate = {};

        _lignePaginate.init = function(el, options = {numberPerPage: 7,goBar:false,pageCounter:true},filter = [{el: null}]
        ){
            setTableEl(el);
            initTable(_lignePaginate.getEl());
            checkIsTableNull();
            setOptions(options);
            setConstNumberPerPage(options.numberPerPage);
            setFilterOptions(filter);
            launchPaginate();
        }

        var settings = {
            el:null,
            table:null,
            numberPerPage:7,
            constNumberPerPage:7,
            numberOfPages:0,
            goBar:false,
            pageCounter:true,
            hasPagination:true,
        };

        var filterSettings = {
            el:null,
            filterBox:null,
            trs:null,
        }

        var setConstNumberPerPage = function(number){
            settings.constNumberPerPage = number;
        }
        var setNumberPerPage = function(number){
            settings.numberPerPage = number;
        }

        var initTable = function(el){
            if(el.indexOf('#') > -1 ){
                settings.table = document.getElementById(el.replace('#','').trim());
            }else if(el.indexOf('.') > -1  ){
                settings.table = document.querySelector(el);
            }
        }

        var iniFilter = function(el){
            if(el.indexOf('#') > -1 ){
                filterSettings.filterBox = document.getElementById(el.replace('#','').trim());
            }else if(el.indexOf('.') > -1  ){
                filterSettings.filterBox = document.querySelector(el);
            }
        }

        var setTableEl = function(el){
            settings.el = el;
        }

        var setFilterOptions = function (filterOptions) {
            if(filterOptions.el != null){
                setFilterEl(filterOptions.el);
                iniFilter(filterSettings.el);
                checkIsFilterBoxNull();
                setFunctionInFilterBox();
            }
        }

        var setFilterEl = function(el){
            filterSettings.el = el;
        }

        var setFunctionInFilterBox = function(){
            filterSettings.filterBox.setAttribute('onkeyup','paginate.filter()')
        }

        var setGoBar = function(value){
            settings.goBar = value;
        }

        var setPageCounter = function(value){
            settings.pageCounter = value;
        }

        _lignePaginate.getEl = function(){
            return settings.el;
        }
        _lignePaginate.getTable = function(){
            return settings.table;
        }
        _lignePaginate.getNumberPerPage = function(){
            return settings.numberPerPage;
        }

        _lignePaginate.getConstNumberPerPage = function(){
            return settings.constNumberPerPage;
        }

        var table,tr = [],pageCount,numberPerPage,th;

        var setOptions = function(options){
            if(options.numberPerPage != settings.numberPerPage){
                setNumberPerPage(options.numberPerPage);
            }

            if(typeof options.goBar === 'boolean')
                setGoBar(options.goBar);

            if(typeof options.pageCounter === 'boolean')
                setPageCounter(options.pageCounter);
        }

        var checkIsTableNull = function(){
            if(settings.table == null){
                throw new Error('Element ' + _lignePaginate.getEl() + ' no exits');
            }
        }

        var checkIsFilterBoxNull = function(){
            if(filterSettings.filterBox == null){
                throw new Error('Element ' + _lignePaginate.getEl() + ' no exits');
            }
        }

        var paginateAlreadyExists = function() {
            let paginate = document.querySelector('div.paginate');
            if(paginate != null)
                removePaginate(paginate);
        }

        var removePaginate = function(element){
            element.parentNode.removeChild(element);
        }

        var hiddenPaginateControls = function(){
            document.querySelector('.paginate_controls').style.visibility = 'hidden';
        }

        var showPaginatecontrols = function(){
            document.querySelector('.paginate_controls').style.visibility = 'unset';
        }

        var pageButtons = function(numberOfPage,currentPage) {

            let	prevDisabled = (currentPage == 1)?"disabled":"";
            let nextDisabled = (currentPage == numberOfPage)?"disabled":"";

            let buttons = "<input type='button' value='← Prev' class='paginate_control_prev' onclick='paginate.sort("+(currentPage - 1)+")' "+prevDisabled+">";

            for (let $i=1; $i<=numberOfPage;$i++){
                if(numberOfPage > 5){
                    buttons += paginationMoreThatTenPage($i,numberOfPage);
                } else {
                    buttons += "<input type='button' id='id"+$i+"'value='"+$i+"' onclick='paginate.sort("+$i+")'>";
                }
            }

            let nextButton = "<input type='button' value='Next →' class='paginate_control_next' onclick='paginate.sort("+(currentPage + 1)+")' "+nextDisabled+">";
            buttons +=  nextButton;

            if(settings.goBar)
                buttons += addGoToPage();

            return buttons;
        }

        var paginationMoreThatTenPage = function(iterator,numberOfPage){

            let referenceForTheLast = numberOfPage - 1;
            let middleValue = '...';

            if(iterator > referenceForTheLast || iterator < 4){
                return "<input type='button' id='id"+iterator+"'value='"+iterator+"' onclick='paginate.sort("+iterator+")'>";
            } else if((iterator + 1) == numberOfPage) {
                return middleValue + "<input type='button' id='id"+iterator+"'value='"+iterator+"' style='display: none' onclick='paginate.sort("+iterator+")'>";
            } else {
                return "<input type='button' id='id"+iterator+"'value='"+iterator+"' style='display: none' onclick='paginate.sort("+iterator+")'>";
            }
        }

        var addGoToPage = function(){
            let inputBox = "<input type='number' id='paginate_page_to_go' value='1' min='1' max='"+ settings.numberOfPages +"'>";
            let goButton = "<input type='button' id='paginate-go-button' value='Go' onclick='paginate.goToPage()'>  ";
            return inputBox + goButton;
        }

        _lignePaginate.goToPage = function(){
            let page = document.getElementById("paginate_page_to_go").value;
            _lignePaginate.sort(page);
        }

        var launchPaginate = function(){
            paginateAlreadyExists();
            table = settings.table;
            numberPerPage = settings.numberPerPage;
            let rowCount = table.rows.length;
            let firstRow = table.rows[0].firstElementChild.tagName;
            let hasHead = (firstRow === "TH");
            let $i,$ii,$j = (hasHead)?1:0;
            th = (hasHead?table.rows[(0)].outerHTML:"");
            pageCount = Math.ceil(rowCount / numberPerPage);
            settings.numberOfPages = pageCount;

            if (pageCount > 1) {
                settings.hasPagination = true;
                for ($i = $j,$ii = 0; $i < rowCount; $i++, $ii++)
                    tr[$ii] = table.rows[$i].outerHTML;

                table.insertAdjacentHTML("afterend","<div id='buttons' class='paginate paginate_controls'></div");

                _lignePaginate.sort(1);
            }else{
                settings.hasPagination = false;
            }
        };

        _lignePaginate.sort = function(selectedPageNumber) {

            let rows = th,startPoint = ((settings.numberPerPage * selectedPageNumber)-settings.numberPerPage);
            for (let $i = startPoint; $i < (startPoint+settings.numberPerPage) && $i < tr.length; $i++)
                rows += tr[$i];

            table.innerHTML = rows;
            document.getElementById("buttons").innerHTML = pageButtons(pageCount,selectedPageNumber);
            document.getElementById("id"+selectedPageNumber).classList.add('active');

            document.getElementById("id"+selectedPageNumber).style.display = 'unset';
        }

        return _lignePaginate;
    }

    if(typeof(window.paginate) === 'undefined'){
        window.paginate = lignePaginate();
    }
})(window);

let options = {
    numberPerPage:7,
    goBar:true,
    pageCounter:true,
};

let filterOptions = {
    el:'#pagination'
};

paginate.init('#myTable',options,filterOptions);