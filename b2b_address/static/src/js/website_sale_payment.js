odoo.define('website_customer_order_delivery_date.payment', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {

        var dat = new Date();
        var date_cal_ini = new Date();
        var date_cal_fin = new Date();

        var currentHour = String(dat.getHours()).padStart(2, "0") + "" + String(dat.getMinutes()).padStart(2, "0");
        var commitment_date = $("#commitment_date").val();
        var commitment_date_js = $("#commitment_date_js").val();
        var lead_time_despacho = $("#lead_time_despacho").val();
        var date_fs = new Date(commitment_date+" 00:00:01");

        console.log("currentHour:",currentHour);
        console.log("commitment_date:",commitment_date);
        console.log("commitment_date_js:",commitment_date_js);
        console.log("lead_time_despacho:",lead_time_despacho);
        console.log("date_fs:",date_fs);

        function CalculaFecha() {
            try {
                date_cal_ini = new Date();
                date_cal_fin = new Date();
                $("#delivery_date").datepicker("destroy");

                var weekday = new Array(7);
                weekday[0] = "Sunday";
                weekday[1] = "Monday";
                weekday[2] = "Tuesday";
                weekday[3] = "Wednesday";
                weekday[4] = "Thursday";
                weekday[5] = "Friday";
                weekday[6] = "Saturday";
                
                var day_week = weekday[dat.getDay()];
                console.log("day_week:",day_week);
                var add_days_date_ini = 2;
                if (parseInt(lead_time_despacho) > add_days_date_ini){
                    add_days_date_ini = parseInt(lead_time_despacho);
                }

                var add_days_date_fin = 15;
                var retiro_en_tienda = $('#retiro_en_tienda').val();
                console.log("retiro_en_tienda:",retiro_en_tienda);

                if(retiro_en_tienda==="true"){
                    add_days_date_ini = 1;
                }

                //SE AGREGAN 3 DIAS SI VIERNES 
                if (day_week == "Friday" ){
                    add_days_date_ini += 2;
                }
                
                //SE AGREGAN 2 DIAS SI ES SABADO
                if (day_week == "Saturday"){
                    add_days_date_ini += 1;
                }

                //SE AGREGAN 1 DIA SI ES DOMINGO
                if (day_week == "Sunday"){
                    add_days_date_ini += 0;
                }

                console.log("add_days_date_ini:",add_days_date_ini);


                //==========VARIABLE QUE GUARDA LA FECHA INICIO Y FIN PERMITIDA
                date_cal_ini.setDate(date_cal_ini.getDate() + add_days_date_ini);
                date_cal_fin.setDate(date_cal_fin.getDate() + add_days_date_fin);


                var day_week_ini = weekday[date_cal_ini.getDay()];
                console.log("day_week_ini:",day_week_ini);
                add_days_date_ini = 0;
                
                //SE AGREGAN 2 DIAS SI ES SABADO
                if (day_week_ini == "Saturday"){
                    add_days_date_ini = 2;
                }

                //SE AGREGAN 1 DIA SI ES DOMINGO
                if (day_week_ini == "Sunday"){
                    add_days_date_ini = 1;
                }
                if(add_days_date_ini > 0 ){
                    date_cal_ini.setDate(date_cal_ini.getDate() + add_days_date_ini);
                }
                
                console.log("date_cal_ini:",date_cal_ini);
                console.log("date_cal_fin:",date_cal_fin);
                //=========== CONFIGURACION DE VALORES MINIMOS Y MAXIMOS DE FECHAS
                $("#delivery_date").datepicker({
                    dateFormat: 'dd/mm/yy',
                    minDate: date_cal_ini,
                    maxDate: date_cal_fin,
                    startDate: date_cal_ini,
                    endDate: date_cal_fin,
                });

                $.datepicker.regional['es'] = {
                    closeText: 'Cerrar',
                    prevText: '< Ant',
                    nextText: 'Sig >',
                    currentText: 'Hoy',
                    monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                    monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
                    dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                    dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
                    dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
                    weekHeader: 'Sm',
                    dateFormat: 'dd/mm/yy',
                    firstDay: 1,
                    isRTL: false,
                    showMonthAfterYear: false,
                    yearSuffix: '',
                    minDate: date_cal_ini,
                    maxDate: date_cal_fin,
                    startDate: date_cal_ini,
                    endDate: date_cal_fin,
                    beforeShowDay: function(date_cal_ini) {
                        var show = true;
                        if(date_cal_ini.getDay()==0 || date_cal_ini.getDay()==6) show=false
                        return [show];
                    },
                };

                //=========== CONFIGURACION REGIONAL
                $.datepicker.setDefaults($.datepicker.regional['es']);
                $( "#delivery_date" ).datepicker( $.datepicker.regional[ "es" ] );
                $( "#locale" ).on( "change", function() {
                    $( "#delivery_date" ).datepicker( "option",
                        $.datepicker.regional[ "es"] );
                });
                
                //FORMATO DE FECHA 
                let date_str = getFormatoFechaLatino(date_cal_ini);

                if(date_fs >= date_cal_ini && date_fs <= date_cal_fin){
                    console.log("update fecha_entrega_fs setDate:",commitment_date_js);
                    $( "#delivery_date" ).datepicker( "setDate", commitment_date_js);
                }else{
                    console.log("delivery_date setDate:",date_str);
                    $( "#delivery_date" ).datepicker( "setDate", date_str);
                }
                
                //MUESTRA DATEPICKER
                $("#delivery_date_icon").click(function(){
                    $('#delivery_date').datepicker('show');
                });

                //ACTUALIZACION DE FECHA DE ENTREGA EN BASE DE DATOS 
                var customer_order_delivery_date = $('#delivery_date').val();
                ajax.jsonRpc('/shop/set_delivery_day', 'call', {
                    'delivery_date': customer_order_delivery_date
                });

            } catch (e) {
                console.log("Error:", e.message);
            }
        }

        CalculaFecha();


        $("input#delivery_date").bind("change", function(ev) {
            var customer_order_delivery_date = $('#delivery_date').val();
            ajax.jsonRpc('/shop/set_delivery_day', 'call', {
                'delivery_date': customer_order_delivery_date
            });

            console.log("customer_order_delivery_date:",customer_order_delivery_date);
        });


        function getFormatoFechaLatino(fecha){
            console.log("getFormatoFechaLatino fecha:",fecha);
            //FORMATO DE FECHA 
            let day = fecha.getDate()
            let month = fecha.getMonth() + 1
            let year = fecha.getFullYear()
            let date_str = ""; 

            if(month < 10){
                date_str = `${day}/0${month}/${year}`;
                if(day < 10){
                    date_str = `0${day}/0${month}/${year}`;
                }
            }else{
                date_str = `${day}/${month}/${year}`;
                if(day < 10){
                    date_str = `0${day}/${month}/${year}`;
                }
            }
            return date_str
        }

        function getFormatoFechaJS(fecha){
            console.log("getFormatoFechaJS fecha:",fecha);
            //FORMATO DE FECHA 
            let day = fecha.getDate()
            let month = fecha.getMonth() + 1
            let year = fecha.getFullYear()
            let date_str = ""; 

            if(month < 10){
                date_str = `${month}/0${day}/${year}`;
                if(day < 10){
                    date_str = `0${month}/0${day}/${year}`;
                }
            }else{
                date_str = `${month}/${day}/${year}`;
                if(day < 10){
                    date_str = `0${month}/${day}/${year}`;
                }
            }
            return date_str
        }
    });

});