#!/usr/bin/env node

// import packages
const { Sequelize, Model, DataTypes } = require('sequelize');
request = require('request')
cheerio = require('cheerio')

// initialize database
const sequelize = new Sequelize('sqlite://everymac.db')
class MacBookPro extends Model {}
MacBookPro.init({
  name: {
    type: DataTypes.STRING,
    primaryKey: true
  },
  introduced: DataTypes.STRING,
  discontinued: DataTypes.STRING,
  order: DataTypes.STRING,
  model: DataTypes.STRING,
  family: DataTypes.STRING,
  id: DataTypes.STRING,
  ram: DataTypes.STRING,
  vram: DataTypes.STRING,
  storage: DataTypes.STRING,
  optical: DataTypes.STRING,
  price: DataTypes.STRING
}, { sequelize, modelName: 'macbookpro', timestamps: false });

// Sync all defined models to the DB
(async () => {
  await sequelize.sync({force: true});
  // console.log('async conplete')
})()

// console.log('Begin request...')
url = 'http://everymac.com/systems/apple/macbook_pro/index-macbookpro.html'
request(url, function(error, response, body) {
  // console.log('Begin parse...')
	$ = cheerio.load(body)
	$("#contentcenter_specs_internalnav_wrapper").each(function(){
		$("table", this).each(function(){
      let introduced, discontinued, order, model, family, id, ram, vram, storage, optical, name, url, price = null
			$("td", this).each(function(i, elem){
        if(i==1) introduced = $(elem).text().replace('*', '')
        else if(i==3) discontinued = $(elem).text().replace('*', '')
        else if(i==5) order = $(elem).text().replace('*', '')
        else if(i==7) model = $(elem).text().replace('*', '')
        else if(i==9) family = $(elem).text().replace('*', '')
        else if(i==11) id = $(elem).text().replace('*', '')
        else if(i==13) ram = $(elem).text().replace('*', '')
        else if(i==15) vram = $(elem).text().replace('*', '')
        else if(i==17) storage = $(elem).text().replace('*', '')
        else if (i==19) optical = $(elem).text().replace('*', '')
        if(i==20) {
          // get name and price
          name = $(elem).children('a').text().split(" ").slice(1, -1).join(" ")
          url = 'http://everymac.com' + $(elem).children('a').attr('href')
          request(url, function(error, response, body) {
            end = body.substr(body.indexOf('<td>US$')+6)
            price = end.substr(0, end.indexOf('<')).replace('*', '')

            /*console.log("Name: " + name)
            console.log("Introduced: " + introduced)
            console.log("Discontinued: " + discontinued)
            console.log("Order: " + order)
            console.log("Model: " + model)
            console.log("Family: " + family)
            console.log("ID: " + id)
            console.log("RAM: " + ram)
            console.log("VRAM: " + vram)
            console.log("Storage: " + storage)
            console.log("Optical: " + optical)
            console.log("Price: " + price);*/

            // create macbook object from parsed data and add to database
            let macbook = MacBookPro.create({
              name: name,
              introduced: introduced,
              discontinued: discontinued,
              order: order,
              model: model,
              family: family,
              id: id,
              ram: ram,
              vram: vram,
              storage: storage,
              optical: optical,
              price: price
            }).then(macbook => {
              console.log(macbook.toJSON());
            });
          })
        }
      }) // end each td
    }) // end each table
    
    // return false will have the script stop after 1 macbook
    //return false;
	}) // end each #contentcenter_specs_internalnav_wrapper
})