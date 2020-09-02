   void draw_fit_hist_and_pull_plot( double& chi2_sum, int& chi2_npoints,
        const char* year_prefix = "",
        const char* bin_name = "D1", bool sig_fit = true, bool draw_sig_norm_1 = false, bool draw_fit_components = false,
        const char* fitfile = "root-files/Fit_Data_2016/output-files/RPV_550_2016/fitDiagnostics2016RPV550.root",
        const char* sig1_name = "RPV 450",
        const char* fitfile_second_signal = "",
        const char* sig2_name = "RPV 650"
        ) {

      bool draw_legend = true ;
      gStyle -> SetOptTitle(0) ;
      gStyle -> SetOptStat(0) ;
      TFile* tf = new TFile( fitfile, "READ" ) ;
      TFile* tf2(0x0) ;
      if ( draw_sig_norm_1 && strlen( fitfile_second_signal ) > 0 ) {
         tf2 = new TFile( fitfile_second_signal, "READ" ) ;
      }

      int hist_nbins ;
      double hist_xv[100] ;
      double hist_yv[100] ;

      double fit_val[100] ;
      double fit_error_high[100] ;
      double fit_error_low[100] ;

      double bkg_val[100] ;
      double sig_val[100] ;

      char fit_type[100] ;
      char fit_middlestring[100] ;
      if ( sig_fit ) {
         sprintf( fit_type, "fit_s" ) ;
         sprintf( fit_middlestring, "" ) ;
      } else {
         sprintf( fit_type, "fit_b" ) ;
         sprintf( fit_middlestring, "_bonly" ) ;
      }

      char hist_title[100] ;
      sprintf( hist_title, "h_%s", bin_name ) ;

      char rpname[100] ;
      sprintf( rpname, "%s_CMS_th1x_%s", bin_name, fit_type ) ;

      RooPlot* rooplot = (RooPlot*) tf -> Get( rpname ) ;
      int nitems = rooplot -> numItems() ;
      for ( int i=0; i<nitems; i++ ) {
         char target_name[100] ;
         char iname[100] ;
         sprintf( iname, "%s", rooplot -> nameOf(i) ) ;
         RooHist* rh = rooplot -> getHist( iname ) ;
         RooCurve* rc = rooplot -> getCurve( iname ) ;
         bool ishist(false) ;
         bool iscurve(false) ;
         if ( rh != 0x0 ) ishist = true ;
         if ( rc != 0x0 ) iscurve = true ;
         double* xv ;
         double* yv ;
         double* xe ;
         double* ye ;
         if ( ishist ) {
            int nbins = rh -> GetN() ;
            if ( strcmp( iname, hist_title ) == 0 ) { hist_nbins = nbins ; }
            xv = rh -> GetX() ;
            yv = rh -> GetY() ;
            xe = rh -> GetEX() ;
            ye = rh -> GetEY() ;
            for ( int pi=0; pi<nbins; pi++ ) {
               if ( strcmp( iname, hist_title ) == 0 ) { hist_xv[pi] = xv[pi] ;  hist_yv[pi] = yv[pi] ; }
            } // pi
         }
         if ( iscurve ) {
            int np = rc -> GetN() ;
            bool is_errorband(false) ;
            sprintf( target_name, "pdf_bin%s%s_Norm[CMS_th1x]_errorband", bin_name, fit_middlestring ) ;
            if ( strcmp( iname, target_name ) == 0 ) is_errorband = true ;
            double* cx = rc -> GetX() ;
            double* cy = rc -> GetY() ;
            if ( is_errorband ) {
               for ( int pi=0; pi<hist_nbins; pi++ ) {
                  double smallest_xdiff ;
                  smallest_xdiff = 1e9 ;
                  for ( int j=0; j<np/2; j++ ) {
                     double xdiff = fabs( hist_xv[pi] - cx[j] ) ;
                     if ( xdiff < smallest_xdiff && xdiff < 0.4 ) {
                        fit_error_high[pi] = cy[j] ;
                     }
                  }
                  for ( int j=np/2; j<np; j++ ) {
                     double xdiff = fabs( hist_xv[pi] - cx[j] ) ;
                     if ( xdiff < smallest_xdiff && xdiff < 0.4 ) {
                        fit_error_low[pi] = cy[j] ;
                     }
                  }
               } // pi
            }
            for ( int pi=0; pi<hist_nbins; pi++ ) {
               double fval = rc -> Eval( hist_xv[pi] ) ;
               int closest_index(0) ;
               double smallest_xdiff(1e9) ;
               for ( int j=0; j<np; j++ ) {
                  double xdiff = fabs( hist_xv[pi] - cx[j] ) ;
                  if ( xdiff < smallest_xdiff ) {
                     closest_index = j ;
                     smallest_xdiff = xdiff ;
                  }
               }

               sprintf( target_name, "pdf_bin%s%s_Norm[CMS_th1x]_Comp[shapeSig*]", bin_name, fit_middlestring ) ;
               if ( strcmp( iname, target_name ) == 0 ) { sig_val[pi] = cy[closest_index] ; }

               sprintf( target_name, "pdf_bin%s%s_Norm[CMS_th1x]_Comp[shapeBkg*]", bin_name, fit_middlestring ) ;
               if ( strcmp( iname, target_name ) == 0 ) { bkg_val[pi] = cy[closest_index] ; }

               sprintf( target_name, "pdf_bin%s%s_Norm[CMS_th1x]", bin_name, fit_middlestring ) ;
               if ( strcmp( iname, target_name ) == 0 ) { fit_val[pi] = cy[closest_index] ; }
            } // pi
         }
      } // i

      char fit_type_string[100] ;

      if ( sig_fit ) {
         sprintf( fit_type_string, "fit_s" ) ;
      } else {
         sprintf( fit_type_string, "fit_b" ) ;
      }

      char hname[1000] ;
      sprintf( hname, "shapes_%s/%s/OTHER", fit_type_string, bin_name ) ;
      TH1F* th_other_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/SIG", fit_type_string, bin_name ) ;
      TH1F* th_sig_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/TT", fit_type_string, bin_name ) ;
      TH1F* th_tt_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/QCD", fit_type_string, bin_name ) ;
      TH1F* th_qcd_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/TTX", fit_type_string, bin_name ) ;
      TH1F* th_ttx_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/total", fit_type_string, bin_name ) ;
      TH1F* th_total_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/total_signal", fit_type_string, bin_name ) ;
      TH1F* th_total_signal_shape = (TH1F*) tf -> Get( hname ) ;
      sprintf( hname, "shapes_%s/%s/total_background", fit_type_string, bin_name ) ;
      TH1F* th_total_background_shape = (TH1F*) tf -> Get( hname ) ;

      th_tt_shape -> SetLineColor( kBlue-6 ) ;
      th_tt_shape -> SetMarkerColor( kBlue-6 ) ;
      th_tt_shape -> SetMarkerSize( 0 ) ;
      th_tt_shape -> SetLineWidth( 1 ) ;
      th_tt_shape -> SetLineStyle( 1 ) ;

      th_qcd_shape -> SetLineColor( kGreen+1 ) ;
      th_qcd_shape -> SetMarkerColor( kGreen+1 ) ;
      th_qcd_shape -> SetMarkerSize( 0 ) ;
      th_qcd_shape -> SetLineWidth( 1 ) ;
      th_qcd_shape -> SetLineStyle( 1 ) ;

      th_ttx_shape -> SetLineColor( kOrange+2 ) ;
      th_ttx_shape -> SetMarkerColor( kOrange+2 ) ;
      th_ttx_shape -> SetMarkerSize( 0 ) ;
      th_ttx_shape -> SetLineWidth( 1 ) ;
      th_ttx_shape -> SetLineStyle( 1 ) ;

      th_other_shape -> SetLineColor( kMagenta+2 ) ;
      th_other_shape -> SetMarkerColor( kMagenta+2 ) ;
      th_other_shape -> SetMarkerSize( 0 ) ;
      th_other_shape -> SetLineWidth( 1 ) ;
      th_other_shape -> SetLineStyle( 1 ) ;

      char objname[100] ;
      sprintf( objname, "norm_%s", fit_type_string ) ;
      RooArgSet* ras = (RooArgSet*) tf -> Get( objname ) ;
      ras -> dump() ;
      TIterator* iter = ras -> createIterator() ;
      RooRealVar* rrv ;

      double fit_err_h[100] ;
      double fit_err_l[100] ;

      double pull_hist_yval[100] ;
      double pull_hist_yerr[100] ;
      double hist_xval[100] ;
      double hist_xerr[100] ;
      double hist_err[100] ;
      double pull_fit_val[100] ;
      double pull_fit_error_high[100] ;
      double pull_fit_error_low[100] ;


      chi2_sum = 0. ;
      chi2_npoints = 0 ;
      for ( int bi=0; bi<hist_nbins; bi++ ) {
         double fv = fit_val[bi] ;
         double he(0) ;
         if ( hist_yv[bi] > 0.5 ) he = sqrt( hist_yv[bi] ) ;
         hist_err[bi] = he ;
         pull_hist_yerr[bi] = 1.0 ;
         hist_xval[bi] = hist_xv[bi] ;
         hist_xerr[bi] = 0.5 ;
         pull_fit_val[bi] = 0. ;
         fit_err_h[bi] = fit_error_high[bi] - fit_val[bi] ;
         fit_err_l[bi] = fit_val[bi] - fit_error_low[bi] ;
         if ( he > 0 ) {
            pull_hist_yval[bi] = (hist_yv[bi] - fv) / he ;
            pull_fit_error_high[bi] = (fit_error_high[bi] - fit_val[bi])/he ;
            pull_fit_error_low[bi]  = (fit_val[bi] - fit_error_low[bi])/he ;
            chi2_sum += pow( pull_hist_yval[bi], 2. ) ;
            chi2_npoints ++ ;
         } else {
            pull_hist_yval[bi] = -99. ;
            pull_fit_error_high[bi] = 0. ;
            pull_fit_error_low[bi]  = 0. ;
         }
      } // bi


      TGraphAsymmErrors* tg_fit = new TGraphAsymmErrors( hist_nbins, hist_xval, fit_val, hist_xerr, hist_xerr, fit_err_h, fit_err_l ) ;
      tg_fit -> SetFillColor( kBlue-10 ) ;
      tg_fit -> SetLineColor( 4 ) ;

      TGraphAsymmErrors* tg_hist = new TGraphAsymmErrors( hist_nbins, hist_xval, hist_yv, hist_xerr, hist_xerr, hist_err, hist_err ) ;
      tg_hist -> SetMarkerStyle(20) ;

      TH1F* th_fit = new TH1F( "th_fit", "", hist_nbins, hist_xval[0] - 0.5, hist_xval[hist_nbins-1]+0.5 ) ;
      for ( int bi=0; bi<hist_nbins; bi++ ) { th_fit -> SetBinContent( bi+1, fit_val[bi] ) ; }
      th_fit -> SetLineColor( kBlue ) ;
      th_fit -> SetLineColor(4) ;
      th_fit -> SetLineWidth( 2 ) ;

      TH1F* th_fit_bkg = new TH1F( "th_fit_bkg", "", hist_nbins, hist_xval[0] - 0.5, hist_xval[hist_nbins-1]+0.5 ) ;
      for ( int bi=0; bi<hist_nbins; bi++ ) { th_fit_bkg -> SetBinContent( bi+1, bkg_val[bi] ) ; }
      th_fit_bkg -> SetLineColor( kRed ) ;
      th_fit_bkg -> SetMarkerColor( kRed ) ;
      th_fit_bkg -> SetMarkerSize( 0 ) ;
      th_fit_bkg -> SetLineWidth( 2 ) ;
      th_fit_bkg -> SetLineStyle( 1 ) ;

      TH1F* th_fit_sig = new TH1F( "th_fit_sig", "", hist_nbins, hist_xval[0] - 0.5, hist_xval[hist_nbins-1]+0.5 ) ;
      for ( int bi=0; bi<hist_nbins; bi++ ) { th_fit_sig -> SetBinContent( bi+1, sig_val[bi] ) ; }
      th_fit_sig -> SetLineColor( 8 ) ;
      th_fit_sig -> SetMarkerColor( 8 ) ;
      th_fit_sig -> SetMarkerSize( 0 ) ;
      th_fit_sig -> SetLineWidth( 3 ) ;
      th_fit_sig -> SetLineStyle( 2 ) ;

      TGraphAsymmErrors* tg_fit_pull = new TGraphAsymmErrors( hist_nbins, hist_xval, pull_fit_val, hist_xerr, hist_xerr, pull_fit_error_high, pull_fit_error_low ) ;
      tg_fit_pull -> SetFillColor( kBlue-10 ) ;

      TGraphAsymmErrors* tg_hist_pull = new TGraphAsymmErrors( hist_nbins, hist_xval, pull_hist_yval, hist_xerr, hist_xerr, pull_hist_yerr, pull_hist_yerr ) ;
      tg_hist_pull -> SetMarkerStyle(20) ;

      TH1F* th_fit_pull = new TH1F( "th_fit_pull", "", hist_nbins, hist_xval[0] - 0.5, hist_xval[hist_nbins-1]+0.5 ) ;
      for ( int bi=0; bi<hist_nbins; bi++ ) { th_fit_pull -> SetBinContent( bi+1, pull_fit_val[bi] ) ; }
      th_fit_pull -> SetLineColor( kBlue ) ;
      th_fit_pull -> SetLineWidth( 3 ) ;

      sprintf( hname, "shapes_prefit/%s/total_signal", bin_name ) ;
      TH1F* th_sig_norm_1 = (TH1F*) tf -> Get( hname ) ;
      if ( th_sig_norm_1 == 0x0 ) { printf( "\n\n *** Can't find signal hist %s\n", hname ) ; gSystem -> Exit( -1 ) ; }
      th_sig_norm_1 -> SetLineWidth(3) ;
      th_sig_norm_1 -> SetLineStyle(2) ;
      th_sig_norm_1 -> SetLineColor(6) ;
      th_sig_norm_1 -> SetMarkerSize(0) ;

      TH1F* th_sig2_norm_1(0x0) ;
      if ( tf2 != 0x0 ) {
         th_sig2_norm_1 = (TH1F*) tf2 -> Get( hname ) ;
         if ( th_sig2_norm_1 == 0x0 ) { printf( "\n\n *** Can't find second signal hist %s\n", hname ) ; gSystem -> Exit( -1 ) ; }
         th_sig2_norm_1 -> SetLineWidth(2) ;
         th_sig2_norm_1 -> SetLineWidth(3) ;
         th_sig2_norm_1 -> SetLineStyle(2) ;
         th_sig2_norm_1 -> SetLineColor(3) ;
         th_sig2_norm_1 -> SetMarkerSize(0) ;
      }

      float pull_y_height = 0.30 ;
      float y_buf = 0.00 ;
      float sf = (1.0-0.3)/0.3;

      float xTitleSize = 0.05; 
      float yTitleSize = 0.05;
      float yTitleOffset = 1.4;
      float xTitleOffset = 3.0;
      float yLabelSize = 0.05;
      float xLabelSize = 0.08;
      float yLabelOffset = 0.02;
      float xLabelOffset = 0.04;

      gStyle -> SetPadTopMargin( 0.1 ) ;
      gStyle -> SetPadBottomMargin( 0.01 ) ;
      TPad* histPad = new TPad( "ph","", 0.01, pull_y_height, 0.99, 0.99 ) ;
      histPad -> Draw() ;

      gStyle -> SetPadTopMargin( 0.01 ) ;
      gStyle -> SetPadBottomMargin( 0.40 ) ;
      TPad* pullPad = new TPad( "pp","", 0.01, 0.01, 0.99, pull_y_height-y_buf ) ;
      pullPad -> Draw() ;

      //--------------
      histPad -> cd() ;

      std::string foutname = "KELVIN_"; foutname += year_prefix; foutname += ".root";
      TFile* kelvin = TFile::Open(foutname.c_str(), "UPDATE");
      kelvin->cd();

      std::string ttname = "ttHist_"; ttname += bin_name;
      th_tt_shape->Write(ttname.c_str());

      std::string qcdname = "qcdHist_"; qcdname += bin_name;
      th_qcd_shape->Write(qcdname.c_str());

      std::string ttxname = "ttxHist_"; ttxname += bin_name;
      th_ttx_shape->Write(ttxname.c_str());

      std::string othername = "otherHist_"; othername += bin_name;
      th_other_shape->Write(othername.c_str());

      std::string dataname = "dataHist_"; dataname += bin_name;
      tg_hist->Write(dataname.c_str());

      std::string bkgname = "bkgdHist_"; bkgname += bin_name;
      th_fit_bkg->Write(bkgname.c_str());

      std::string signame = "sigHist_"; signame += bin_name;
      th_fit_sig->Write(signame.c_str());

      std::string signame1 = "sigRefHist1_"; signame1 += bin_name;
      th_sig_norm_1->Write(signame1.c_str());

      std::string signame2 = "sigRefHist2_"; signame2 += bin_name;
      th_sig2_norm_1->Write(signame2.c_str());

      th_fit -> SetYTitle( "Events" ) ;
      th_fit -> SetTitleSize( yTitleSize, "y" ) ;
      th_fit -> SetTitleOffset( yTitleOffset, "y" ) ;
      th_fit -> SetLabelSize( yLabelSize, "y" ) ;

      for ( int bi=0; bi<hist_nbins; bi++ ) {
         char binlabel[100] ;
         if ( bi < (hist_nbins-1) ) {
            sprintf( binlabel, "%d", bi+7 ) ;
         } else {
            sprintf( binlabel, "%d+", bi+7 ) ;
         }
         th_fit -> GetXaxis() -> SetBinLabel( bi+1, binlabel ) ;
      } // bi

      th_fit -> SetMaximum( 5.0 * (th_fit -> GetMaximum()) ) ;
      th_fit -> SetMinimum(0.05) ;

      std::string fitname = "Fit_"; fitname += bin_name;
      tg_fit->Write(fitname.c_str());

      std::string nobsname = "Nobs_"; nobsname += bin_name;
      tg_hist->Write(nobsname.c_str());

      th_fit -> Draw( "hist" ) ;
      tg_fit -> Draw( "2" ) ;
      th_fit -> Draw( "same hist" ) ;
      th_fit -> Draw( "axis same" ) ;
      th_fit -> Draw( "axig same" ) ;
      if ( draw_sig_norm_1 ) th_sig_norm_1 -> Draw("hist same" ) ;
      if ( draw_sig_norm_1 && th_sig2_norm_1 != 0x0 ) th_sig2_norm_1 -> Draw("hist same" ) ;
      if ( draw_fit_components ) {
         th_fit_bkg -> Draw( "hist same" ) ;
         th_fit_sig -> Draw( "hist same" ) ;
      }
      tg_hist -> Draw( "p" ) ;
      gPad -> SetLogy(1) ;

      TText* text = new TText() ;
      char title[1000] ;
      sprintf( title, "MVA bin %s", bin_name ) ;
      text -> DrawTextNDC( 0.15, 0.91, title ) ;

      if ( draw_legend ) {
         float legend_item_dy = 0.050 ;
         int n_legend_items = 2 ;
         tg_hist -> SetFillColor( kWhite ) ;
         if ( draw_sig_norm_1 ) n_legend_items ++ ;
         if ( draw_sig_norm_1 && th_sig2_norm_1 != 0x0 ) n_legend_items ++ ;
         if ( draw_fit_components ) n_legend_items += 2 ;
         TLegend* legend = new TLegend( 0.53, ( 0.88 - legend_item_dy * n_legend_items ),  0.88, 0.88 ) ;
         legend -> AddEntry( tg_fit, "Fit" ) ;
         legend -> AddEntry( tg_hist, "N observed" ) ;
         if ( draw_fit_components ) {
            legend -> AddEntry( th_fit_bkg, "Fit Background" ) ;
            legend -> AddEntry( th_fit_sig, "Fit Signal" ) ;
         }
         char sig1[100] ;
         sprintf( sig1, "Signal, %s", sig1_name ) ;
         if ( draw_sig_norm_1 ) legend -> AddEntry( th_sig_norm_1, sig1 ) ;
         if ( draw_sig_norm_1 && th_sig2_norm_1 != 0x0 ) {
            char sig2[100] ;
            sprintf( sig2, "Signal, %s", sig2_name ) ;
            legend -> AddEntry( th_sig2_norm_1, sig2 ) ;
         }
         legend -> Draw() ;
      }

      TText* tt2 = new TText() ;
      char str[100] ;
      sprintf( str, "chi2 = %7.2f", chi2_sum ) ;
      tt2 -> DrawTextNDC( 0.40, 0.11, str ) ;

      //--------------
      pullPad -> cd() ;

      th_fit_pull -> SetMinimum( -3.5 ) ;
      th_fit_pull -> SetMaximum( 3.5 ) ;
      th_fit_pull -> SetYTitle( "#frac{val - fit}{#sigma_{val}}" ) ;
      th_fit_pull -> SetXTitle( "Number of jets" ) ;
      th_fit_pull -> SetTitleSize( xTitleSize*sf, "x" ) ;
      th_fit_pull -> SetTitleSize( yTitleSize*sf, "y" ) ;
      th_fit_pull -> SetTitleOffset( yTitleOffset/sf, "y" ) ;
      th_fit_pull -> SetTitleOffset( xTitleOffset/sf, "x" ) ;
      th_fit_pull -> SetLabelOffset( xLabelOffset/sf, "x" ) ;
      th_fit_pull -> SetLabelOffset( yLabelOffset/sf, "y" ) ;
      th_fit_pull -> SetLabelSize( xLabelSize*sf, "x" ) ;
      th_fit_pull -> SetLabelSize( yLabelSize*sf, "y" ) ;
      th_fit_pull -> GetYaxis() -> SetNdivisions( 404 ) ;
      for ( int bi=0; bi<hist_nbins; bi++ ) {
         char binlabel[100] ;
         if ( bi < (hist_nbins-1) ) {
            sprintf( binlabel, "%d", bi+7 ) ;
         } else {
            sprintf( binlabel, "%d+", bi+7 ) ;
         }
         th_fit_pull -> GetXaxis() -> SetBinLabel( bi+1, binlabel ) ;
      } // bi


      TLine* line = new TLine() ;
      line -> SetLineColor(2) ;
      line -> SetLineWidth(1) ;

      std::string pullname = "pulls_"; pullname += bin_name;
      std::string pullerrname = "pullsErr_"; pullerrname += bin_name;

      tg_fit_pull->Write(pullerrname.c_str());
      tg_hist_pull->Write(pullname.c_str());

      tg_fit_pull -> SetLineWidth(1) ;
      th_fit_pull -> SetLineWidth(1) ;

      th_fit_pull -> Draw( "hist" ) ;
      tg_fit_pull -> Draw( "2" ) ;
      th_fit_pull -> Draw( "same hist" ) ;
      th_fit_pull -> Draw( "axis same" ) ;
      th_fit_pull -> Draw( "axig same" ) ;
      tg_hist_pull -> Draw( "p" ) ;
      gPad -> SetGridx(1) ;
      gPad -> SetGridy(1) ;


      kelvin->Close();

   } // print_fit_result

