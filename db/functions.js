function giveCount(id){
  db.vegas.findAndModify({
      query: {"_id":find},
      update: {
          $inc: {"count": 1},
      },
      writeConcern: 'majority'
  });
  return db.vegas.findOne({"_id":id}).count;
}

function updateSubs(status){
  db.settings.updateOne({}, {"$set":{"submit":status}});
}

function updateToken(token){
  db.settings.updateOne({}, {"$set":{"token":token}});
}

function updateTime(t){
  db.settings.updateOne({}, {"$set":{"timeSub":t}});
}

//Vegas document example
{
  "_id":"",
  "count":0,
  "battle":"Splinter#4298VSFrank Whoee#1334",
  "author":"Splinter#4298"
}
