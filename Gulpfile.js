'use strict';

var gulp = require('gulp');
var gulpBrowser = require('gulp-browser');
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');
var sass = require('gulp-sass');

// tasks

gulp.task('sass', function () {
  return gulp.src('app/static/css/sass/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('app/static/css/css'));
});
 
gulp.task('watch', function () {
  gulp.watch('app/static/css/sass/**/*.scss', ['sass']);
});

gulp.task('default', ['watch']);