using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Web;

namespace DataEmulator
{

    public class orderdetails
    { 
        public int id { get; set; } 

        public int quantity { get; set; }
        public string? name { get; set; }

        public double? price { get; set; }
    }
    public class Order
    {
        public string? id { get; set; }

        public DateTime orderDate { get; set; }

        public orderdetails []? orderdetails { get; set; }

        public string? storeId { get; set; }

        public bool cloudSynced { get; set; }
    }

    public class Product
    {
        public string? id { get; set; }
        public string? name { get; set;}
        public double? price { get; set;}
        public int stock { get; set; }
        public string? photopath { get; set; }
        public string? category { get; set; }
    }

    public class Store
    {
        public string? StoreLocation { get; set; }
        public string? id { get; set; }
    }
}
